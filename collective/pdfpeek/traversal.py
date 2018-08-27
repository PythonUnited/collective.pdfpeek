# -*- coding: utf-8 -*-
from collective.pdfpeek.interfaces import IPDF
from plone.namedfile.utils import set_headers, stream_data
from zope.component import adapts
from zope.interface import implements
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.interfaces import ITraversable


class PDFPeekImageScaleTraverser(object):
    """Used to traverse to images stored on IPDF objects

    Traversing to portal/object/++pdfpeekimages++/++page++1 will retrieve the first
    page of the pdf, acquisition-wrapped.
    """
    implements(ITraversable)
    adapts(IPDF, IHTTPRequest)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        annotations = dict(self.context.__annotations__)
        image = annotations['pdfpeek']['image_thumbnails'][name]

        # Try determine blob name and default to "context_id_download."
        # This is only visible if the user tried to save the file to local
        # computer.
        filename = getattr(image, 'filename', name)

        # Sets Content-Type and Content-Length
        set_headers(image, self.request.response)

        # Set Content-Disposition
        self.request.response.setHeader(
            'Content-Disposition',
            'inline; filename={0}'.format(filename)
        )
        return stream_data(image)
