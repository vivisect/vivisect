import sys

import cobra.unittests

# Import order here is by test run order!
import cobra.unittests.basictest as c_basictest
import cobra.unittests.msgpacktest as c_msgpacktest
import cobra.unittests.reftest as c_reftest
import cobra.unittests.authtest as c_authtest
import cobra.unittests.shadowtest as c_shadowtest

def main():
    cobra.unittests.runUnitTests()

if __name__ == '__main__':
    sys.exit(main())
