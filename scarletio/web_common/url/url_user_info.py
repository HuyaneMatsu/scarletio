__all__ = ()

from ...utils import RichAttributeErrorBaseType

from .url_part_base import URLPartBase


class URLUserInfo(RichAttributeErrorBaseType):
    """
    Represents the user information of an url.
    
    Attributes
    ----------
    _name : `None | URLPartBase`
        The user's name if any.
    
    _password : `None | URLPartBase`
        The user's password if any.
    """
    __slots__ = ('_name', '_password')
    
    
    def __new__(cls):
        """
        Use either ``.create_from_decoded`` or ``.create_from_encoded`` instead.
        
        Raises
        ------
        RuntimeError
        """
        raise RuntimeError(
            'Use either `.create_from_decoded` or `.create_from_encoded` instead.'
        )
    
    
    def __repr__(self):
        """Returns the url path's representation."""
        repr_parts = ['<', type(self).__name__]
        
        field_added = False
        
        # name_decoded
        name_decoded = self.name_decoded
        if (name_decoded is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' name_decoded = ')
            repr_parts.append(repr(name_decoded))
        
        # password_decoded
        password_decoded = self.password_decoded
        if (password_decoded is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' password_decoded = ')
            repr_parts.append(repr(password_decoded))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two url parts are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # name
        if self._name != other._name:
            return False
        
        # password
        if self._password != other._password:
            return False
        
        return True
    
    
    @classmethod
    def create_from_decoded(cls, user_name, user_password):
        """
        Creates a new url user info from decoded values.
        
        Parameters
        ----------
        user_name : `None | str`
            The user's name.
        
        user_password : `None | str`
            The user's password.
        
        Returns
        -------
        self : `instance<cls>`
        """
        if user_name is None:
            name = None
        else:
            name = URLPartBase.create_from_decoded(user_name)
        
        if user_password is None:
            password = None
        else:
            password = URLPartBase.create_from_decoded(user_password)
        
        self = object.__new__(cls)
        self._name = name
        self._password = password
        return self
    
    
    @classmethod
    def create_from_encoded(cls, user_name, user_password):
        """
        Creates a new url user info from encoded values.
        
        Parameters
        ----------
        user_name : `None | str`
            The user's name.
        
        user_password : `None | str`
            The user's password.
        
        Returns
        -------
        self : `instance<cls>`
        """
        if user_name is None:
            name = None
        else:
            name = URLPartBase.create_from_encoded(user_name)
        
        if user_password is None:
            password = None
        else:
            password = URLPartBase.create_from_encoded(user_password)
        
        self = object.__new__(cls)
        self._name = name
        self._password = password
        return self
    
    
    @property
    def name_decoded(self):
        """
        Returns the user info's decoded name.
        
        Returns
        -------
        name : `None | str`
        """
        name = self._name
        if (name is not None):
            return name.decoded
    
    
    @property
    def password_decoded(self):
        """
        Returns the user info's decoded password.
        
        Returns
        -------
        name : `None | str`
        """
        password = self._password
        if (password is not None):
            return password.decoded

    
    @property
    def name_encoded(self):
        """
        Returns the user info's encoded name.
        
        Returns
        -------
        name : `None | str`
        """
        name = self._name
        if (name is not None):
            return name.encoded
    
    
    @property
    def password_encoded(self):
        """
        Returns the user info's encoded password.
        
        Returns
        -------
        name : `None | str`
        """
        password = self._password
        if (password is not None):
            return password.encoded
