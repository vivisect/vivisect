import io
import unittest

import vivisect.storage.common as v_storage
#import vivisect.workspace as v_workspace

class VivFileTests(unittest.TestCase):

    def test_vivfile_basics(self):

        blob = io.BytesIO(b'AAAAAAAA')

        st = v_storage.getVivStore('ram://')
        vf = st.addVivFile( blob )

        loc1 = vf.getLocByAddr(1,add=True)
        loc2 = vf.getLocByAddr(2,add=True)
        ref1 = vf.getRefByDef( 1,'code',2,add=True)

        vf.setLocProp(loc1,'woot',10)
        vf.setLocProp(loc2,'woot',20)
        vf.setRefProp(ref1,'foo','bar')

        self.assertEqual( len(vf.getLocsByProp('woot')), 2 )
        self.assertEqual( len(vf.getLocsByProp('woot',20)), 1 )
        self.assertEqual( len(vf.getRefsByProp('foo','bar')), 1 )

        vf = st.getVivFile(vf.filemd5)
        self.assertEqual( len(vf.getLocsByProp('woot')), 2 )
        self.assertEqual( len(vf.getLocsByProp('woot',20)), 1 )
        self.assertEqual( len(vf.getRefsByProp('foo','bar')), 1 )
