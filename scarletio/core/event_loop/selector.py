__all__ = ()

import sys
from selectors import DefaultSelector
from threading import current_thread


if sys.platform == 'win32':
    # If windows select raises OSError, we cannot do anything, but if it it raises ValueError, we can increases
    # windows select() from 500~ till the hard limit, with sharding up it's polls
    
    from select import select
    MAX_FD_S = 500 #512 is the actual amount?
    MAX_SLEEP = 0.001
    EMPTY = []
    
    class DefaultSelector(DefaultSelector):
        """
        Selector subclass for windows to bypass default limit.
        
        Note, that this selector might become CPU heavy if the limit is passed and the sockets might become closed
        if too much is open.
        
        I do not take credit for any misbehaviour.
        """
        def _select(self, r, w, _, timeout = None):
            try:
                result_r, result_w, result_x = select(r, w, w, timeout)
            except ValueError:
                default_reader = current_thread()._self_read_socket
                r.remove(default_reader.fileno())
                
                sharded_r = []
                sharded_w = []
                
                sharded = [(sharded_r, sharded_w,),]
                
                count = 0
                for reader in r:
                    if count == MAX_FD_S:
                        sharded_r = [reader]
                        sharded_w = []
                        sharded.append((sharded_r, sharded_w),)
                        count = 1
                    else:
                        sharded_r.append(reader)
                        count = count + 1
                
                for writer in w:
                    if count == MAX_FD_S:
                        sharded_r = []
                        sharded_w = [writer]
                        sharded.append((sharded_r, sharded_w),)
                        count = 1
                    else:
                        sharded_w.append(writer)
                        count += 1
                
                collected_r = []
                collected_w = []
                
                r.add(default_reader.fileno())
                
                for iter_r, iter_w in sharded:
                    try:
                        result_r, result_w, result_x = select(iter_r, iter_w, iter_w, 0.0)
                    except OSError:
                        remove = []
                        for reader in iter_r:
                            try:
                                l = [reader]
                                result_r, result_w, result_x = select(l, EMPTY, EMPTY, 0.0)
                            except OSError:
                                remove.append(reader)
                            else:
                                if result_r:
                                    collected_r.append(result_r[0])
                        
                        if remove:
                            for reader in remove:
                                r.discard(reader)
                                
                                try:
                                    self.unregister(reader)
                                except KeyError:
                                    pass
                            remove.clear()
                        
                        for writer in iter_w:
                            try:
                                l = [writer]
                                result_r, result_w, result_x = select(EMPTY, l, l, 0.0)
                            except OSError:
                                remove.append(writer)
                            else:
                                if result_w:
                                    collected_w.append(result_w[0])
                                elif result_x:
                                    collected_w.append(result_x[0])
                        
                        if remove:
                            for writer in remove:
                                w.discard(writer)
                                
                                try:
                                    self.unregister(writer)
                                except KeyError:
                                    pass
                            remove.clear()
                    else:
                        collected_r.extend(result_r)
                        collected_w.extend(result_w)
                        collected_w.extend(result_x)

                if (not collected_r) and (not collected_w):
                    if timeout is None:
                        timeout = MAX_SLEEP
                    elif timeout < 0.0:
                        timeout = 0.0
                    elif timeout > MAX_SLEEP:
                        timeout = MAX_SLEEP
                    
                    result_r, result_w, result_x = select([default_reader], EMPTY, EMPTY, timeout)
                    collected_r.extend(result_r)
                
                return collected_r, collected_w, EMPTY
            
            except OSError:
                collected_r = []
                collected_w = []
                do_later_r = []
                do_later_w = []
                remove = []
                for reader in r:
                    try:
                        l = [reader]
                        result_r, result_w, result_x = select(l, EMPTY, EMPTY, 0.0)
                    except OSError:
                        remove.append(reader)
                    else:
                        if result_r:
                            collected_r.append(result_r[0])
                        else:
                            do_later_r.append(reader)
                
                if remove:
                    for reader in remove:
                        r.discard(reader)
                        
                        try:
                            self.unregister(reader)
                        except KeyError:
                            pass
                    remove.clear()
                    
                for writer in w:
                    try:
                        l = [writer]
                        result_r, result_w, result_x = select(EMPTY, l, l, 0.0)
                    except OSError:
                        remove.append(writer)
                    else:
                        if result_w:
                            collected_w.append(result_w[0])
                        elif result_x:
                            collected_w.append(result_x[0])
                        else:
                            do_later_w.append(writer)
                    
                if remove:
                    for writer in remove:
                        w.discard(writer)
                        
                        try:
                            self.unregister(writer)
                        except KeyError:
                            pass
                    remove.clear()
                
                if collected_r or collected_w:
                    return collected_r, collected_w, EMPTY
                
                result_r, result_w, result_x = select(r, w, w, timeout)
                result_w.extend(result_x)
                return result_r, result_w, EMPTY
            else:
                result_w.extend(result_x)
                return result_r, result_w, EMPTY
