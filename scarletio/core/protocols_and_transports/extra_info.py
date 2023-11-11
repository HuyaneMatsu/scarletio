__all__ = ()

EXTRA_INFO_NAME_SSL_CONTEXT = 'ssl_context'
EXTRA_INFO_NAME_SSL_OBJECT = 'ssl_object'
EXTRA_INFO_NAME_SOCKET = 'socket'
EXTRA_INFO_NAME_PEER_CERTIFICATION = 'peer_certification'
EXTRA_INFO_NAME_CIPHER = 'cipher'
EXTRA_INFO_NAME_COMPRESSION = 'compression'
EXTRA_INFO_NAME_SOCKET_NAME = 'socket_name'
EXTRA_INFO_NAME_PEER_NAME = 'peer_name'
EXTRA_INFO_NAME_PIPE = 'pipe'

ALTERNATIVE_EXTRA_INFO_NAMES = {
    EXTRA_INFO_NAME_SSL_CONTEXT: 'ssl_context',
    EXTRA_INFO_NAME_SOCKET: 'sock',
    EXTRA_INFO_NAME_PEER_CERTIFICATION: 'peercert',
    EXTRA_INFO_NAME_SOCKET_NAME: 'sockname',
    EXTRA_INFO_NAME_PEER_NAME: 'peername',
}

def get_extra_info(extra, name, default):
    """
    Gets optional transport information.
    
    Parameters
    ----------
    extra : `None`, `dict` of (`str`, `object`) items
        Optional transform information.
    name : `str`
        The extra information's name to get.
    default : `object`
        Default value to return if `name` could not be matched. Defaults to `None`.
    
    Returns
    -------
    info : `default`, `object`
    """
    if extra is None:
        info = None
    else:
        try:
            info = extra[name]
        except KeyError:
            try:
                name = ALTERNATIVE_EXTRA_INFO_NAMES[name]
            except KeyError:
                info = default
            else:
                info = extra.get(name, default)
    
    return info


def set_extra_info(extra, name, value):
    """
    Sets optional transport information.
    
    Parameters
    ----------
    extra : `None`, `dict` of (`str`, `object`) items
        Optional transform information.
    name : `str`
        The extra info's name.
    value : `object`
        The value to set.
    
    Returns
    -------
    extra : `dict` of (`str`, `object`) items
        The new transform information.
    """
    if extra is None:
        extra = {}
    
    extra[name] = value
    
    return extra


def has_extra_info(extra, name):
    """
    Checks optional transport information.
    
    Parameters
    ----------
    extra : `None`, `dict` of (`str`, `object`) items
        Optional transform information.
    name : `str`
        The extra info's name.
    
    Returns
    -------
    has_extra_info : `bool`
        Whether the transport has the extra information.
    """
    if extra is None:
        has_extra_info = False
    else:
        if name in extra:
            has_extra_info = True
        else:
            try:
                name = ALTERNATIVE_EXTRA_INFO_NAMES[name]
            except KeyError:
                has_extra_info = False
            else:
                has_extra_info = (name in extra)
    
    return has_extra_info


def get_has_extra_info(extra, name):
    """
    Gets optional transport information and whether it is present, or nah.
    
    Parameters
    ----------
    extra : `None`, `dict` of (`str`, `object`) items
        Optional transform information.
    name : `str`
        The extra information's name to get.
    
    Returns
    -------
    info : `default`, `object`
        Optional transport information.
    present : `bool`
        Whether the field is present.
    """
    if extra is None:
        info = None
        present = False
    else:
        try:
            info = extra[name]
        except KeyError:
            try:
                name = ALTERNATIVE_EXTRA_INFO_NAMES[name]
            except KeyError:
                info = None
                present = False
            else:
                try:
                    info = extra[name]
                except KeyError:
                    info = None
                    present = False
                else:
                    present = True
        
        else:
            present = True
        
    return info, present
