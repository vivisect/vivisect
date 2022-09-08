import socket

import vstruct
from vstruct.primitives import *
import vstruct.defs.inet as vs_inet

# only the currently parsed record types
DNS_TYPE_A     = 1
DNS_TYPE_NS    = 2
DNS_TYPE_CNAME = 5
DNS_TYPE_SOA   = 6
DNS_TYPE_PTR   = 12
DNS_TYPE_MX    = 15
DNS_TYPE_TXT   = 16
DNS_TYPE_RP    = 17
DNS_TYPE_AFSDB = 18
DNS_TYPE_SIG   = 24
DNS_TYPE_KEY   = 25
DNS_TYPE_AAAA  = 28
DNS_TYPE_LOC   = 29
DNS_TYPE_SRV   = 33
DNS_TYPE_NAPTR = 35
DNS_TYPE_KX    = 36
DNS_TYPE_CERT  = 37
DNS_TYPE_DNAME = 39

DNS_TYPE_OPT   = 41
DNS_TYPE_APL   = 42
DNS_TYPE_DS    = 43
DNS_TYPE_SSHFP = 44
DNS_TYPE_IPSECKEY = 45
DNS_TYPE_RRSIG = 46
DNS_TYPE_NSEC  = 47
DNS_TYPE_DNSKEY= 48
DNS_TYPE_DHCID = 49

DNS_TYPE_NSEC3 = 50
DNS_TYPE_NSEC3PARAM = 51
DNS_TYPE_TLSA  = 52
DNS_TYPE_HIP   = 55
DNS_TYPE_CDS   = 59
DNS_TYPE_CDNSKEY = 60

DNS_TYPE_TKEY  = 249
DNS_TYPE_TSIG  = 250
DNS_TYPE_IXFR  = 251
DNS_TYPE_AXFR  = 252
DNS_TYPE_ANY   = 255
DNS_TYPE_URI   = 256
DNS_TYPE_CAA   = 257

DNS_TYPE_TA    = 32768
DNS_TYPE_DLV   = 32769

dns_type_names = {
    DNS_TYPE_A:     'A',
    DNS_TYPE_NS:    'NS',
    DNS_TYPE_CNAME: 'CNAME',
    DNS_TYPE_SOA:   'SOA',
    DNS_TYPE_PTR:   'PTR',
    DNS_TYPE_MX:    'MX',
    DNS_TYPE_TXT:   'TXT',
    DNS_TYPE_RP    : 'RP',
    DNS_TYPE_AFSDB : 'AFSDB',
    DNS_TYPE_SIG   : 'SIG',
    DNS_TYPE_KEY   : 'KEY',
    DNS_TYPE_AAAA  : 'AAAA',
    DNS_TYPE_LOC   : 'LOC',
    DNS_TYPE_SRV   : 'SRV',
    DNS_TYPE_NAPTR : 'NAPTR',
    DNS_TYPE_KX    : 'KX',
    DNS_TYPE_CERT  : 'CERT',
    DNS_TYPE_DNAME : 'DNAME',
    DNS_TYPE_OPT   : 'OPT',
    DNS_TYPE_APL   : 'APL',
    DNS_TYPE_DS    : 'DS',
    DNS_TYPE_SSHFP : 'SSHFP',
    DNS_TYPE_IPSECKEY : 'IPSECKEY',
    DNS_TYPE_RRSIG : 'RRSIG',
    DNS_TYPE_NSEC  : 'NSEC',
    DNS_TYPE_DNSKEY: 'DNSKEY',
    DNS_TYPE_DHCID : 'DHCID',
    DNS_TYPE_NSEC3 : 'NSEC3',
    DNS_TYPE_NSEC3PARAM : 'NSEC3PARAM',
    DNS_TYPE_TLSA  : 'TLSA',
    DNS_TYPE_HIP   : 'HIP',
    DNS_TYPE_CDS   : 'CDS',
    DNS_TYPE_CDNSKEY : 'CDNSKEY',
    DNS_TYPE_TKEY  : 'TKEY',
    DNS_TYPE_TSIG  : 'TSIG',
    DNS_TYPE_IXFR  : 'IXFR',
    DNS_TYPE_AXFR  : 'AXFR',
    DNS_TYPE_ANY   : 'ANY',
    DNS_TYPE_URI   : 'URI',
    DNS_TYPE_CAA   : 'CAA',
    DNS_TYPE_TA    : 'TA',
    DNS_TYPE_DLV   : 'DLV',
}

DNS_CLASS_IN     = 1
DNS_CLASS_CSNET  = 2
DNS_CLASS_CHAOS  = 3
DNS_CLASS_HESIOD = 4
DNS_CLASS_ANY    = 255

dns_class_names = {
    DNS_CLASS_IN     : 'IN',
    DNS_CLASS_CSNET  : 'CSNET',
    DNS_CLASS_CHAOS  : 'CHAOS',
    DNS_CLASS_HESIOD : 'HESIOD',
    DNS_CLASS_ANY    : 'ANY',
}

DNS_NAMETYPE_LABEL        = 0
DNS_NAMETYPE_RESERVED     = 1
DNS_NAMETYPE_EXTENDED     = 2 
DNS_NAMETYPE_POINTER      = 3
DNS_NAMETYPE_LABELPOINTER = 4

DNS_FLAG_RESP   = 1 << 15
DNS_FLAG_TRUNC  = 1 << 9
DNS_FLAG_RECUR  = 1 << 8
#DNS_FLAG_AA = 1 << 5    # authoritative answer
#DNS_FLAG_TC = 1 << 6    # truncated response
#DNS_FLAG_RD = 1 << 7    # recursion desired
#DNS_FLAG_RA = 1 << 8    # recursion allowed
#DNS_FLAG_AD = 1 << 10   # authentic data
#DNS_FLAG_CD = 1 << 11   # checking disabled

#totally arbitrary count value to abort parsing dns records
DNS_SUSPICIOUS_COUNT = 0x20

class DnsParseError(Exception):
    pass

def dnsFlagsOp(val):
    return (val >> 11) & 0xf

class DnsNameLabel(vstruct.VStruct):
    '''
    A DNS Name component.
    '''
    def __init__(self, label=''):
        vstruct.VStruct.__init__(self)
        self._nametype = 0
        self._pointer  = 0
        self.length = v_uint8( len(label) )
        self.label  = v_bytes( vbytes=label )

    def pcb_length(self):
        size = self.length
        labeltype = size >> 6
        # ordered by use
        if labeltype == 0b11:
            self._nametype = DNS_NAMETYPE_POINTER
            size = 1
        elif labeltype == 0b00:
            self._nametype = DNS_NAMETYPE_LABEL
        elif labeltype == 0b10:
            raise DnsParseError('Extended labeltype is not supported.') 
        elif labeltype == 0b01:
            raise DnsParseError('Unrecognized labeltype (reserved).')
        self.vsGetField('label').vsSetLength(size)

    def pcb_label(self):
        if self.length == 0:
            return
        if self._nametype == DNS_NAMETYPE_POINTER:
            ordlabel = 0
            # some broken(?) packets have a pointer with an empty label
            if self.label:
                ordlabel = ord(self.label)
            # the length field's lower 6 bits + the 8 bits from the label form the pointer
            self._pointer = ((self.length ^ 0xc0) << 8) + ordlabel

    def getNameType(self):
        return self._nametype

    def getNamePointer(self):
        return self._pointer

    def isNamePointer(self):
        if self._nametype == DNS_NAMETYPE_POINTER:
            return True
        return False

    def isNameTerm(self):
        if self.length == 0 or self._nametype == DNS_NAMETYPE_POINTER:
            return True
        return False

class DnsName(vstruct.VArray):
    '''
    The contiguous labels (DnsNameLabel()) in a DNS Name field.  Note that the
    last label may simply be a pointer to an offset earlier in the DNS message.
    '''
    def __init__(self, name=None):
        vstruct.VArray.__init__(self)
        if name is not None:
            for part in name.split('.'):
                self.vsAddElement( DnsNameLabel( part ) )
            self.vsAddElement( DnsNameLabel('') )

    def getTypeVal(self):
        '''
        Return a (nametype, nameval) tuple based on walking the labels.
        '''
        nametype = None
        namepointer = None
        labels = []
        for fname,fobj in self.vsGetFields():
            nametype = fobj.getNameType()
            if nametype == DNS_NAMETYPE_LABEL and fobj.length != 0:
                labels.append(fobj.label)
            if nametype == DNS_NAMETYPE_POINTER:
                namepointer = fobj.getNamePointer()
                if labels:
                    nametype = DNS_NAMETYPE_LABELPOINTER

        joinedlabels = '.'.join(labels)
        if nametype == DNS_NAMETYPE_LABEL:
            return nametype,joinedlabels
        elif nametype == DNS_NAMETYPE_POINTER:
            return nametype,namepointer
        elif nametype == DNS_NAMETYPE_LABELPOINTER:
            return nametype,(joinedlabels,namepointer)
        raise DnsParseError('Unrecognized label.')

    def vsParse(self, bytez, offset=0):
        while offset < len(bytez):
            nl = DnsNameLabel()
            labelofs = offset
            offset = nl.vsParse(bytez, offset=offset)
            self.vsAddElement(nl)
            if nl.isNamePointer() and nl.getNamePointer() >= labelofs:
                raise DnsParseError('Label points forward (or to self).')
            if nl.isNameTerm():
                break
        return offset

class DnsMailboxAsName(DnsName):
    '''
    A DNS Name used to encode a mailbox address.
    '''
    pass

class DnsQuestion(vstruct.VStruct):
    '''
    A DNS Question Record (the query).
    '''
    def __init__(self, name=None, qtype=0, qclass=0):
        vstruct.VStruct.__init__(self)
        self.qname  = DnsName(name=name)
        self.qtype  = v_uint16(qtype, bigend=True)
        self.qclass = v_uint16(qclass, bigend=True)

class DnsQuestionArray(vstruct.VArray):
    '''
    A DNS Question Section.
    '''
    def __init__(self, reccnt):
        vstruct.VArray.__init__(self)
        for i in range(reccnt):
            self.vsAddElement(DnsQuestion())

class DnsResourceRecord(vstruct.VStruct):
    '''
    A DNS Resource Record.  Used in the Answer, Authority, and Additional Sections.
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.dnsname  = DnsName()
        self.rrtype   = v_uint16(bigend=True)
        self.dnsclass = v_uint16(bigend=True)
        self.ttl      = v_uint32(bigend=True)
        self.rdlength = v_uint16(bigend=True)
        self.rdata    = vstruct.VStruct()

    def pcb_rrtype(self):
        if self.rrtype == DNS_TYPE_A:
            self.rdata.address = vs_inet.IPv4Address()
        elif self.rrtype == DNS_TYPE_AAAA:
            self.rdata.address = vs_inet.IPv6Address()
        elif self.rrtype == DNS_TYPE_NS:
            self.rdata.nsdname = DnsName()
        elif self.rrtype == DNS_TYPE_CNAME:
            self.rdata.cname = DnsName()
        elif self.rrtype == DNS_TYPE_SOA:
            self.rdata.mname   = DnsName()
            # this is an encoded email address 
            self.rdata.rname   = DnsMailboxAsName()
            self.rdata.serial  = v_uint32(bigend=True)
            self.rdata.refresh = v_uint32(bigend=True)
            self.rdata.retry   = v_uint32(bigend=True)
            self.rdata.expire  = v_uint32(bigend=True)
            self.rdata.minimum = v_uint32(bigend=True)
        elif self.rrtype == DNS_TYPE_PTR:
            self.rdata.ptrdname = DnsName()
        elif self.rrtype == DNS_TYPE_MX:
            self.rdata.preference = v_uint16(bigend=True)
            self.rdata.exchange   = DnsName()
        elif self.rrtype == DNS_TYPE_TXT:
            self.rdata.txtdata = v_str()
        else:
            self.rdata.bytez = v_bytes()

    def pcb_rdlength(self):
        size = self.rdlength
        if self.rdata.vsHasField('bytez'):
            self.rdata.vsGetField('bytez').vsSetLength(size)
        elif self.rdata.vsHasField('txtdata'):
            self.rdata.vsGetField('txtdata').vsSetLength(size)


class DnsResourceRecordArray(vstruct.VArray):
    '''
    A DNS RR Section (Answer, Authority, or Additional).
    '''
    def __init__(self, reccnt):
        vstruct.VArray.__init__(self)
        for i in range(reccnt):
            self.vsAddElement(DnsResourceRecord())

class DnsMessage(vstruct.VStruct):
    '''
    A DNS Message.
    '''
    def __init__(self, tcpdns=False):
        vstruct.VStruct.__init__(self)
        self._tcpdns = tcpdns
        if tcpdns:
            self.length = v_uint16(bigend=True)
        self.transid  = v_uint16(bigend=True)
        self.flags    = v_uint16(bigend=True)
        self.qdcount  = v_uint16(bigend=True)
        self.ancount  = v_uint16(bigend=True)
        self.nscount  = v_uint16(bigend=True)
        self.arcount  = v_uint16(bigend=True)
        self.section  = vstruct.VStruct()
        self.section.question   = DnsQuestionArray(0)
        self.section.answer     = DnsResourceRecordArray(0)
        self.section.authority  = DnsResourceRecordArray(0)
        self.section.additional = DnsResourceRecordArray(0)
        self._nptr = {}  # name pointer cache

        #cached question & answers
        self._cache_qrs = None
        self._cache_ars = None

    def pcb_qdcount(self):
        if self.qdcount > DNS_SUSPICIOUS_COUNT:
            raise RuntimeError('DNS suspicious count threshold hit')
        self.section.question = DnsQuestionArray(self.qdcount)

    def pcb_ancount(self):
        if self.ancount > DNS_SUSPICIOUS_COUNT:
            raise RuntimeError('DNS suspicious count threshold hit')
        self.section.answer = DnsResourceRecordArray(self.ancount)

    def pcb_nscount(self):
        if self.nscount > DNS_SUSPICIOUS_COUNT:
            raise RuntimeError('DNS suspicious count threshold hit')
        self.section.authority = DnsResourceRecordArray(self.nscount)

    def pcb_arcount(self):
        if self.arcount > DNS_SUSPICIOUS_COUNT:
            raise RuntimeError('DNS suspicious count threshold hit')
        self.section.additional = DnsResourceRecordArray(self.arcount)

    def vsParse(self, bytez, offset=0):
        self._cache_qrs = None
        self._cache_ars = None
        self._dns_bytes = bytez
        self._dns_offset = offset
        return vstruct.VStruct.vsParse(self, bytez, offset=offset)

    def _getLabelPointerRef(self, msgofs):
        '''
        Given an offset relative to the beginning of a message, create a
        DnsName() structure based on the data there, and return the results
        of its getTypeVal() method (a (nametype, nameval) tuple).
        '''
        # msgofs is relative to the beginning of the message, not necessarily the stream
        if msgofs not in self._nptr:
            # these are often repeated within a message, so we cache them
            self._nptr[msgofs] = DnsName()
            self._nptr[msgofs].vsParse(self._dns_bytes, self._dns_offset + msgofs)
        return self._nptr[msgofs].getTypeVal()

    def getDnsName(self, nametype, nameval):
        '''
        Given a nametype (one of the DNS_NAMETYPE_* constants) and nameval
        (depending on the type, either an fqdn, pointer, or partial fqdn and
        a pointer), return an fqdn.  This is meant to be called with the
        results from a DnsName() instance's getTypeVal() method.
        '''
        if nametype == DNS_NAMETYPE_LABEL:
            fqdn = nameval

        elif nametype == DNS_NAMETYPE_POINTER:
            offset = nameval
            if self._tcpdns:
                # if we're a TCP packet, the 'length' field is not included in the pointer offset
                offset += 2

            fqdn = self.getDnsName(*self._getLabelPointerRef(offset))

        elif nametype == DNS_NAMETYPE_LABELPOINTER:
            beginlabels,offset = nameval
            if self._tcpdns:
                # if we're a TCP packet, the 'length' field is not included in the pointer offset
                offset += 2

            ptrtype,ptrval = self._getLabelPointerRef(offset)
            endlabels = self.getDnsName(ptrtype, ptrval)
            fqdn = '.'.join((beginlabels, endlabels))
        return fqdn

    def getQuestionRecords(self):
        '''
        Return a list of Question records as (dnstype, dnsclass, fqdn) tuples.
        '''
        if self._cache_qrs:
            return self._cache_qrs
        ret = []
        for fname,q in self.section.question.vsGetFields():
            fqdn = self.getDnsName(*q.qname.getTypeVal())
            ret.append((q.qtype, q.qclass, fqdn))
        self._cache_qrs = ret
        return ret

    def _getResourceRecords(self, structure):
        '''
        Given a DnsResourceRecordArray() structure, return a list of Resource 
        Records as (dnstype, dnsclass, ttl, fqdn, adata) tuples.  If a parser
        is available for the dnsclass, the 'rdata' field will be further parsed 
        into its components (as a tuple if necessary).
        '''
        ret = []
        for fname,rr in structure.vsGetFields():
            fqdn = self.getDnsName(*rr.dnsname.getTypeVal())

            rdata = None
            if rr.rrtype == DNS_TYPE_A:
                rdata = vs_inet.reprIPv4Addr(rr.rdata.address)
            elif rr.rrtype == DNS_TYPE_AAAA:
                rdata = vs_inet.reprIPv6Addr(rr.rdata.address)
            elif rr.rrtype == DNS_TYPE_NS:
                rdata = self.getDnsName(*rr.rdata.nsdname.getTypeVal())
            elif rr.rrtype == DNS_TYPE_CNAME:
                rdata = self.getDnsName(*rr.rdata.cname.getTypeVal())
            elif rr.rrtype == DNS_TYPE_SOA:
                rdata = (self.getDnsName(*rr.rdata.mname.getTypeVal()),
                         self.getDnsName(*rr.rdata.rname.getTypeVal()),
                         rr.rdata.serial,
                         rr.rdata.refresh,
                         rr.rdata.retry, 
                         rr.rdata.expire,
                         rr.rdata.minimum)
            elif rr.rrtype == DNS_TYPE_PTR:
                rdata = self.getDnsName(*rr.rdata.ptrdname.getTypeVal())
            elif rr.rrtype == DNS_TYPE_MX:
                rdata = (rr.rdata.preference,
                         self.getDnsName(*rr.rdata.exchange.getTypeVal()))
            elif rr.rrtype == DNS_TYPE_TXT:
                rdata = rr.rdata.txtdata
            else:
                rdata = rr.rdata.bytez

            ret.append((rr.rrtype, rr.dnsclass, rr.ttl, fqdn, rdata))
        return ret

    def getAnswerRecords(self):
        '''
        Return a list of Answer records as (rrtype, dnsclass, ttl, fqdn,
        rdata) tuples.  If a parser is available for the dnsclass, the 
        'rdata' field will be further parsed into its components (as a
        tuple if necessary).
        '''
        if not self._cache_ars:
            self._cache_ars = self._getResourceRecords(structure=self.section.answer)
        return self._cache_ars

    def getAuthorityRecords(self):
        '''
        Return a list of Authority records as (rrtype, dnsclass, ttl, 
        fqdn, rdata) tuples.  If a parser is available for the dnsclass, 
        the 'rdata' field will be further parsed into its components 
        (as a tuple if necessary).
        '''
        return self._getResourceRecords(structure=self.section.authority)

    def getAdditionalRecords(self):
        '''
        Return a list of Additional records as (rrtype, dnsclass, ttl, 
        fqdn, rdata) tuples.  If a parser is available for the dnsclass, 
        the 'rdata' field will be further parsed into its components (as 
        a tuple if necessary).
        '''
        return self._getResourceRecords(structure=self.section.additional)

    def getDnsNames(self):
        '''
        Return a list of the DNS names in the message.
        '''
        fqdns = set()
        for ofs,indent,fname,fobj in self.vsGetPrintInfo():
            if fobj.vsGetTypeName() == 'DnsName':
                fqdns.add(self.getDnsName(*fobj.getTypeVal()))
        return list(fqdns)

    def getIPv4Integers(self):
        '''
        Return a list of the IPv4 addresses in the message.
        '''
        ips = set()
        for ofs,indent,fname,fobj in self.vsGetPrintInfo():
            if fobj.vsGetTypeName() == 'IPv4Address':
                ips.add(fobj._vs_value)
        return list(ips)

    def getEmailAddresses(self):
        '''
        Return a list of the email addresses which are encoded as DNS names
        in the message (they are decoded back to email addresses here).
        '''
        emails = set()
        for ofs,indent,fname,fobj in self.vsGetPrintInfo():
            if fobj.vsGetTypeName() == 'DnsMailboxAsName':
                mailbox = self.getDnsName(*fobj.getTypeVal())
                parts = mailbox.split('.', 1)
                emails.add('@'.join(parts))
        return list(emails)
