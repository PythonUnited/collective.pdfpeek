# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from collective.pdfpeek.async import get_queue
from zc.lockfile import LockError
from zc.lockfile import LockFile
from zope.interface import Interface
from pkg_resources import parse_version
from zope.interface import alsoProvides

import logging
import os
import tempfile
import pkg_resources

try:
    plone_protect = pkg_resources.get_distribution('plone.protect')
    if parse_version(plone_protect.version) < parse_version('3.0'):
        HAS_PLONE_PROTECT = False
    else:
        from plone.protect.interfaces import IDisableCSRFProtection
        HAS_PLONE_PROTECT = True
except pkg_resources.DistributionNotFound:
    HAS_PLONE_PROTECT = False

LOCKFILE_NAME = os.path.join(tempfile.gettempdir(),
                             __name__ + '.process_conversion_queue')

logger = logging.getLogger('collective.pdfpeek.browser.utils')


class IpdfpeekUtilView(Interface):

    def process_conversion_queue(self):
        """process the queue.
        This is what you call from cron or zope clock server to get
        periodic image preview generation.
        """


class pdfpeekUtilView(BrowserView):

    def process_conversion_queue(self):
        """process the queue.
        """
        if HAS_PLONE_PROTECT:
            # Disabling CSRF protection
            alsoProvides(self.request, IDisableCSRFProtection)

        try:
            lock = LockFile(LOCKFILE_NAME)
        except LockError:
            return '`process_conversion_queue` is locked by another ' + \
                   'process ({0}).'.format(LOCKFILE_NAME)

        try:
            return self._process_conversion_queue()
        finally:
            lock.close()

    def _process_conversion_queue(self):
        msg = u''
        num = 0
        queue = get_queue('collective.pdfpeek.conversion_' + self.context.id)
        num = queue.process()
        if num:
            msg += u'%d Jobs in queue. Processing queue...\n' % num
            for job in queue.finished[-1:]:
                msg += job.value + u'\n'
                msg += u'Finished Job'
        if num == 0:
            msg += u'No Jobs in Queue. No Action Required, None Taken.'
        return msg
