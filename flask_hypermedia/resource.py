from typing import Mapping, List, Union, Any, Optional
from flask import request
from dataclasses import dataclass
from types import SimpleNamespace

@dataclass
class Link:
    rel: str
    href: str
    templated: Optional[bool] = None
    name: Optional[str] = None

    def to_hal(self):
        hal = {'href': self.href}
        if self.templated is not None:
            hal['templated'] = self.templated
        if self.name is not None:
            hal['name'] = self.name
        return hal

class Resource:
    """
    A resource which is intended be rendered as either HAL+JSON or as HTMX+HTML
    """

    links: SimpleNamespace[Union[Link,List[Link]]]
    """
    A set of links, which specify all actions that can be taken on this resource given the current 
    context of user permissions and resource state.

    The keys of this dict are the link's relation to the resource (e.g. the HTML `rel` attribute, 
    see https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel). However, you are not
    nessesarilly limited to the "official" rel values; you may define your own as CURIEs if an 
    official rel can't be found. (See https://stateless.group/hal_specification.html)

    At minimum, this should always contain a 'self' link.
    """

    data: SimpleNamespace
    """
    The data belonging directly to this resource. All items should be JSON-encodable.
    """

    embedded: Optional[SimpleNamespace[Union['Resource',List['Resource']]]] = None
    """
    Any embedded sub-resources.

    If this resource is a collection, then the items in the collection will be stored here.

    If this resource is a single entity, then the embedded resources can still be used to store 
    related resources.
    """

    def __init__(self, links: Mapping[str,Union[Link,List[Link]]], data: Optional[Mapping[str,Any]] = None, embedded: Optional[Mapping[str,Union['Resource',List['Resource']]]] = None):
        self.links = SimpleNamespace(**links)
        self.data = SimpleNamespace(**data) if data is not None else SimpleNamespace()
        self.embedded = SimpleNamespace(**embedded) if embedded is not None else None

    @classmethod
    def for_request(cls, links: Optional[Mapping[str,Union[Link,List[Link]]]] = None, *args, **kwargs):
        """
        Alternate constructor that populates the 'self' link from the current request.
        """
        if links is None:
            links = {}
        if 'self' not in links:
            links.self = request.url
        return cls(links, *args, **kwargs)
    
    def to_hal(self)->dict:
        """
        Convert this resource to its Hypertext Application Language representation
        """
        hal = {
            '_links': {
                key: link.to_hal() if isinstance(link, Link) else [item.to_hal() for item in link]
                for key, link in self.links.__dict__.items()
            },
            **self.data.__dict__
        }
        if self.embedded is not None:
            hal['_embedded'] = {
                key: resource.to_hal() if isinstance(resource, Resource) else [item.to_hal() for item in resource]
                for key, resource in self.embedded.__dict__.items()
            }
        return hal

    def link(self, rel: str, link: Union[Link,str], *args, **kwargs):
        """
        Add a link to the resource
        """
        if not isinstance(link, Link):
            link = Link(rel, link, *args, **kwargs)
        if rel in self.links.__dict__:
            if isinstance(self.links.__dict__[rel], list):
                self.links.__dict__[rel].append(link)
            else:
                self.links.__dict__[rel] = [
                    self.links.__dict__[rel],
                    link,
                ]
        else:
            self.links.__dict__[rel] = link
        return self



