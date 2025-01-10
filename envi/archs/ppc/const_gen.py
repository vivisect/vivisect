FIELD_BD = 0
FIELD_BH = 1
FIELD_BI = 2
FIELD_BO = 3
FIELD_CRM = 4
FIELD_CT = 5
FIELD_D = 6
FIELD_DCRN0_4 = 7
FIELD_DCRN5_9 = 8
FIELD_DCTL = 9
FIELD_DE = 10
FIELD_DS = 11
FIELD_DUI = 12
FIELD_E = 13
FIELD_FM = 14
FIELD_IU = 15
FIELD_LEV = 16
FIELD_LI = 17
FIELD_MB = 18
FIELD_ME = 19
FIELD_MO = 20
FIELD_OC = 21
FIELD_OU = 22
FIELD_PMRN0_4 = 23
FIELD_PMRN5_9 = 24
FIELD_SA = 25
FIELD_SIMM16 = 26
FIELD_SIMM5 = 27
FIELD_SPRN0_4 = 28
FIELD_SPRN5_9 = 29
FIELD_SS = 30
FIELD_STRM = 31
FIELD_T = 32
FIELD_TBRN0_4 = 33
FIELD_TBRN5_9 = 34
FIELD_TH = 35
FIELD_TMRN0_4 = 36
FIELD_TMRN5_9 = 37
FIELD_TO = 38
FIELD_W = 39
FIELD_WC = 40
FIELD_WH = 41
FIELD_crBI = 42
FIELD_crD = 43
FIELD_crb = 44
FIELD_crbA = 45
FIELD_crbB = 46
FIELD_crbC = 47
FIELD_crbD = 48
FIELD_crfD = 49
FIELD_frA = 50
FIELD_frB = 51
FIELD_frC = 52
FIELD_frD = 53
FIELD_frS = 54
FIELD_mb0 = 55
FIELD_mb1_5 = 56
FIELD_me0 = 57
FIELD_me1_5 = 58
FIELD_rA = 59
FIELD_sA = 60
FIELD_rB = 61
FIELD_sB = 62
FIELD_rC = 63
FIELD_sC = 64
FIELD_rD = 65
FIELD_sD = 66
FIELD_rS = 67
FIELD_sS = 68
FIELD_sh0 = 69
FIELD_sh1_5 = 70
FIELD_vA = 71
FIELD_vB = 72
FIELD_vC = 73
FIELD_vD = 74
FIELD_vS = 75
FIELD_IMM = 76
FIELD_L = 77
FIELD_SH = 78
FIELD_SIMM = 79
FIELD_UIMM = 80
FIELD_UIMM1 = 81
FIELD_UIMM2 = 82
FIELD_UIMM3 = 83
FIELD_crfS = 84

CAT_NONE = 1<<0
CAT_64 = 1<<1
CAT_E = 1<<2
CAT_V = 1<<3
CAT_SP = 1<<4
CAT_SP_FV = 1<<5
CAT_SP_FS = 1<<6
CAT_SP_FD = 1<<7
CAT_EMBEDDED = 1<<8
CAT_E_ED = 1<<9
CAT_E_HV = 1<<10
CAT_E_PD = 1<<11
CAT_ER = 1<<12
CAT_WT = 1<<13
CAT_E_CL = 1<<14
CAT_E_PC = 1<<15
CAT_ISAT = 1<<16
CAT_E_DC = 1<<17
CAT_E_PM = 1<<18
CAT_EM_TM = 1<<19
CAT_DS = 1<<20
CAT_FP = 1<<21
CAT_DEO = 1<<22
CAT_FP_R = 1<<23

CATEGORIES = { y : x  for x,y in globals().items() if x.startswith("CAT_")}

FORM_A = 0
FORM_B = 1
FORM_D = 2
FORM_DS = 3
FORM_EVX = 4
FORM_I = 5
FORM_M = 6
FORM_MD = 7
FORM_MDS = 8
FORM_SC = 9
FORM_VA = 10
FORM_VC = 11
FORM_VX = 12
FORM_X = 13
FORM_XFX = 14
FORM_XL = 15
FORM_XO = 16
FORM_XS = 17
FORM_X_2 = 18

form_names = {
    0 : 'FORM_A',
    1 : 'FORM_B',
    2 : 'FORM_D',
    3 : 'FORM_DS',
    4 : 'FORM_EVX',
    5 : 'FORM_I',
    6 : 'FORM_M',
    7 : 'FORM_MD',
    8 : 'FORM_MDS',
    9 : 'FORM_SC',
    10 : 'FORM_VA',
    11 : 'FORM_VC',
    12 : 'FORM_VX',
    13 : 'FORM_X',
    14 : 'FORM_XFX',
    15 : 'FORM_XL',
    16 : 'FORM_XO',
    17 : 'FORM_XS',
    18 : 'FORM_X_2',
}

mnems = (
    'add',
    'addb',
    'addbss',
    'addbu',
    'addbus',
    'addc',
    'addco',
    'adde',
    'addeo',
    'addh',
    'addhss',
    'addhu',
    'addhus',
    'addi',
    'addic',
    'addis',
    'addme',
    'addmeo',
    'addo',
    'addw',
    'addwss',
    'addwu',
    'addwus',
    'addze',
    'addzeo',
    'and',
    'andc',
    'andi',
    'andis',
    'b',
    'ba',
    'bc',
    'bca',
    'bcctr',
    'bcctrl',
    'bcl',
    'bcla',
    'bclr',
    'bclrl',
    'bctr',
    'bctrl',
    'bdnz',
    'bdnzeq',
    'bdnzeql',
    'bdnzeqlr',
    'bdnzeqlrl',
    'bdnzge',
    'bdnzgel',
    'bdnzgelr',
    'bdnzgelrl',
    'bdnzgt',
    'bdnzgtl',
    'bdnzgtlr',
    'bdnzgtlrl',
    'bdnzl',
    'bdnzle',
    'bdnzlel',
    'bdnzlelr',
    'bdnzlelrl',
    'bdnzlr',
    'bdnzlrl',
    'bdnzlt',
    'bdnzltl',
    'bdnzltlr',
    'bdnzltlrl',
    'bdnzne',
    'bdnznel',
    'bdnznelr',
    'bdnznelrl',
    'bdnzns',
    'bdnznsl',
    'bdnznslr',
    'bdnznslrl',
    'bdnzso',
    'bdnzsol',
    'bdnzsolr',
    'bdnzsolrl',
    'bdz',
    'bdzeq',
    'bdzeql',
    'bdzeqlr',
    'bdzeqlrl',
    'bdzge',
    'bdzgel',
    'bdzgelr',
    'bdzgelrl',
    'bdzgt',
    'bdzgtl',
    'bdzgtlr',
    'bdzgtlrl',
    'bdzl',
    'bdzle',
    'bdzlel',
    'bdzlelr',
    'bdzlelrl',
    'bdzlr',
    'bdzlrl',
    'bdzlt',
    'bdzltl',
    'bdzltlr',
    'bdzltlrl',
    'bdzne',
    'bdznel',
    'bdznelr',
    'bdznelrl',
    'bdzns',
    'bdznsl',
    'bdznslr',
    'bdznslrl',
    'bdzso',
    'bdzsol',
    'bdzsolr',
    'bdzsolrl',
    'beq',
    'beqctr',
    'beqctrl',
    'beql',
    'beqlr',
    'beqlrl',
    'bge',
    'bgectr',
    'bgectrl',
    'bgel',
    'bgelr',
    'bgelrl',
    'bgt',
    'bgtctr',
    'bgtctrl',
    'bgtl',
    'bgtlr',
    'bgtlrl',
    'bl',
    'bla',
    'ble',
    'blectr',
    'blectrl',
    'blel',
    'blelr',
    'blelrl',
    'blr',
    'blrl',
    'blt',
    'bltctr',
    'bltctrl',
    'bltl',
    'bltlr',
    'bltlrl',
    'bne',
    'bnectr',
    'bnectrl',
    'bnel',
    'bnelr',
    'bnelrl',
    'bns',
    'bnsctr',
    'bnsctrl',
    'bnsl',
    'bnslr',
    'bnslrl',
    'bpermd',
    'brinc',
    'bso',
    'bsoctr',
    'bsoctrl',
    'bsol',
    'bsolr',
    'bsolrl',
    'cmp',
    'cmpb',
    'cmpd',
    'cmpdi',
    'cmpi',
    'cmpl',
    'cmpld',
    'cmpldi',
    'cmpli',
    'cmplw',
    'cmplwi',
    'cmpw',
    'cmpwi',
    'cntlzd',
    'cntlzw',
    'crand',
    'crandc',
    'creqv',
    'crnand',
    'crnor',
    'cror',
    'crorc',
    'crxor',
    'dcba',
    'dcbal',
    'dcbf',
    'dcbfep',
    'dcbi',
    'dcblc',
    'dcblq',
    'dcbst',
    'dcbstep',
    'dcbt',
    'dcbtep',
    'dcbtls',
    'dcbtst',
    'dcbtstep',
    'dcbtstls',
    'dcbz',
    'dcbzep',
    'dcbzl',
    'dcbzlep',
    'divd',
    'divdo',
    'divdu',
    'divduo',
    'divw',
    'divwe',
    'divweo',
    'divweu',
    'divweuo',
    'divwo',
    'divwu',
    'divwuo',
    'dnh',
    'dni',
    'dsn',
    'dss',
    'dssall',
    'dst',
    'dstst',
    'dststt',
    'dstt',
    'efdabs',
    'efdadd',
    'efdcfs',
    'efdcfsf',
    'efdcfsi',
    'efdcfuf',
    'efdcfui',
    'efdcmpeq',
    'efdcmpgt',
    'efdcmplt',
    'efdctsf',
    'efdctsi',
    'efdctsiz',
    'efdctuf',
    'efdctui',
    'efdctuiz',
    'efddiv',
    'efdmul',
    'efdnabs',
    'efdneg',
    'efdsub',
    'efdtsteq',
    'efdtstgt',
    'efdtstlt',
    'efsabs',
    'efsadd',
    'efscfd',
    'efscfh',
    'efscfsf',
    'efscfsi',
    'efscfuf',
    'efscfui',
    'efscmpeq',
    'efscmpgt',
    'efscmplt',
    'efsctsf',
    'efsctsi',
    'efsctsiz',
    'efsctuf',
    'efsctui',
    'efsctuiz',
    'efsdiv',
    'efsmadd',
    'efsmsub',
    'efsmul',
    'efsnabs',
    'efsneg',
    'efssub',
    'efststeq',
    'efststgt',
    'efststlt',
    'ehpriv',
    'eqv',
    'esync',
    'evabs',
    'evaddiw',
    'evaddsmiaaw',
    'evaddssiaaw',
    'evaddumiaaw',
    'evaddusiaaw',
    'evaddw',
    'evand',
    'evandc',
    'evcmpeq',
    'evcmpgts',
    'evcmpgtu',
    'evcmplts',
    'evcmpltu',
    'evcntlsw',
    'evcntlzw',
    'evdivws',
    'evdivwu',
    'eveqv',
    'evextsb',
    'evextsh',
    'evfsabs',
    'evfsadd',
    'evfscfsf',
    'evfscfsi',
    'evfscfuf',
    'evfscfui',
    'evfscmpeq',
    'evfscmpgt',
    'evfscmplt',
    'evfsctsf',
    'evfsctsi',
    'evfsctsiz',
    'evfsctuf',
    'evfsctui',
    'evfsctuiz',
    'evfsdiv',
    'evfsmul',
    'evfsnabs',
    'evfsneg',
    'evfssub',
    'evfststeq',
    'evfststgt',
    'evfststlt',
    'evldd',
    'evlddepx',
    'evlddx',
    'evldh',
    'evldhx',
    'evldw',
    'evldwx',
    'evlhhesplat',
    'evlhhesplatx',
    'evlhhossplat',
    'evlhhossplatx',
    'evlhhousplat',
    'evlhhousplatx',
    'evlwhe',
    'evlwhex',
    'evlwhos',
    'evlwhosx',
    'evlwhou',
    'evlwhoux',
    'evlwhsplat',
    'evlwhsplatx',
    'evlwwsplat',
    'evlwwsplatx',
    'evmergehi',
    'evmergehilo',
    'evmergelo',
    'evmergelohi',
    'evmhegsmfaa',
    'evmhegsmfan',
    'evmhegsmiaa',
    'evmhegsmian',
    'evmhegumiaa',
    'evmhegumian',
    'evmhesmf',
    'evmhesmfa',
    'evmhesmfaaw',
    'evmhesmfanw',
    'evmhesmi',
    'evmhesmia',
    'evmhesmiaaw',
    'evmhesmianw',
    'evmhessf',
    'evmhessfa',
    'evmhessfaaw',
    'evmhessfanw',
    'evmhessiaaw',
    'evmhessianw',
    'evmheumi',
    'evmheumia',
    'evmheumiaaw',
    'evmheumianw',
    'evmheusiaaw',
    'evmheusianw',
    'evmhogsmfaa',
    'evmhogsmfan',
    'evmhogsmiaa',
    'evmhogsmian',
    'evmhogumiaa',
    'evmhogumian',
    'evmhosmf',
    'evmhosmfa',
    'evmhosmfaaw',
    'evmhosmfanw',
    'evmhosmi',
    'evmhosmia',
    'evmhosmiaaw',
    'evmhosmianw',
    'evmhossf',
    'evmhossfa',
    'evmhossfaaw',
    'evmhossfanw',
    'evmhossiaaw',
    'evmhossianw',
    'evmhoumi',
    'evmhoumia',
    'evmhoumiaaw',
    'evmhoumianw',
    'evmhousiaaw',
    'evmhousianw',
    'evmra',
    'evmwhsmf',
    'evmwhsmfa',
    'evmwhsmi',
    'evmwhsmia',
    'evmwhssf',
    'evmwhssfa',
    'evmwhumi',
    'evmwhumia',
    'evmwlsmiaaw',
    'evmwlsmianw',
    'evmwlssiaaw',
    'evmwlssianw',
    'evmwlumi',
    'evmwlumia',
    'evmwlumiaaw',
    'evmwlumianw',
    'evmwlusiaaw',
    'evmwlusianw',
    'evmwsmf',
    'evmwsmfa',
    'evmwsmfaa',
    'evmwsmfan',
    'evmwsmi',
    'evmwsmia',
    'evmwsmiaa',
    'evmwsmian',
    'evmwssf',
    'evmwssfa',
    'evmwssfaa',
    'evmwssfan',
    'evmwumi',
    'evmwumia',
    'evmwumiaa',
    'evmwumian',
    'evnand',
    'evneg',
    'evnor',
    'evor',
    'evorc',
    'evrlw',
    'evrlwi',
    'evrndw',
    'evsel',
    'evslw',
    'evslwi',
    'evsplatfi',
    'evsplati',
    'evsrwis',
    'evsrwiu',
    'evsrws',
    'evsrwu',
    'evstdd',
    'evstddepx',
    'evstddx',
    'evstdh',
    'evstdhx',
    'evstdw',
    'evstdwx',
    'evstwhe',
    'evstwhex',
    'evstwho',
    'evstwhox',
    'evstwwe',
    'evstwwex',
    'evstwwo',
    'evstwwox',
    'evsubfsmiaaw',
    'evsubfssiaaw',
    'evsubfumiaaw',
    'evsubfusiaaw',
    'evsubfw',
    'evsubifw',
    'evxor',
    'extsb',
    'extsh',
    'extsw',
    'fabs',
    'fadd',
    'fadds',
    'fcfid',
    'fcmpo',
    'fcmpu',
    'fctid',
    'fctidz',
    'fctiw',
    'fctiwz',
    'fdiv',
    'fdivs',
    'fmadd',
    'fmadds',
    'fmr',
    'fmsub',
    'fmsubs',
    'fmul',
    'fmuls',
    'fnabs',
    'fneg',
    'fnmadd',
    'fnmadds',
    'fnmsub',
    'fnmsubs',
    'fres',
    'frsp',
    'frsqrte',
    'fsel',
    'fsub',
    'fsubs',
    'hwsync',
    'icbi',
    'icbiep',
    'icblc',
    'icblq',
    'icbt',
    'icbtls',
    'isel',
    'iseleq',
    'iselgt',
    'isellt',
    'isync',
    'la',
    'lbarx',
    'lbdx',
    'lbepx',
    'lbz',
    'lbzu',
    'lbzux',
    'lbzx',
    'ld',
    'ldarx',
    'ldbrx',
    'lddx',
    'ldepx',
    'ldu',
    'ldux',
    'ldx',
    'lfd',
    'lfddx',
    'lfdepx',
    'lfdu',
    'lfdux',
    'lfdx',
    'lfs',
    'lfsu',
    'lfsux',
    'lfsx',
    'lha',
    'lharx',
    'lhau',
    'lhaux',
    'lhax',
    'lhbrx',
    'lhdx',
    'lhepx',
    'lhz',
    'lhzu',
    'lhzux',
    'lhzx',
    'li',
    'lis',
    'lmw',
    'lvebx',
    'lvehx',
    'lvepx',
    'lvepxl',
    'lvewx',
    'lvexbx',
    'lvexhx',
    'lvexwx',
    'lvsl',
    'lvsm',
    'lvsr',
    'lvswx',
    'lvswxl',
    'lvtlx',
    'lvtlxl',
    'lvtrx',
    'lvtrxl',
    'lvx',
    'lvxl',
    'lwa',
    'lwarx',
    'lwaux',
    'lwax',
    'lwbrx',
    'lwdx',
    'lwepx',
    'lwsync',
    'lwz',
    'lwzu',
    'lwzux',
    'lwzx',
    'mbar',
    'mcrf',
    'mcrfs',
    'mcrxr',
    'mfcr',
    'mfdcr',
    'mffs',
    'mfmsr',
    'mfocrf',
    'mfpmr',
    'mfspr',
    'mftb',
    'mftmr',
    'mfvscr',
    'miso',
    'mr',
    'msgclr',
    'msgsnd',
    'msync',
    'mtcr',
    'mtcrf',
    'mtdcr',
    'mtfsb0',
    'mtfsb1',
    'mtfsf',
    'mtfsfi',
    'mtmsr',
    'mtocrf',
    'mtpmr',
    'mtspr',
    'mttmr',
    'mtvscr',
    'mulhd',
    'mulhdu',
    'mulhss',
    'mulhus',
    'mulhw',
    'mulhwu',
    'mulld',
    'mulldo',
    'mulli',
    'mullw',
    'mullwo',
    'mulwss',
    'mulwus',
    'mvidsplt',
    'mviwsplt',
    'nand',
    'neg',
    'nego',
    'nop',
    'nor',
    'not',
    'or',
    'orc',
    'ori',
    'oris',
    'popcntb',
    'popcntd',
    'popcntw',
    'prtyd',
    'prtyw',
    'rfci',
    'rfdi',
    'rfgi',
    'rfi',
    'rfmci',
    'rldcl',
    'rldcr',
    'rldic',
    'rldicl',
    'rldicr',
    'rldimi',
    'rlwimi',
    'rlwinm',
    'rlwnm',
    'sat',
    'sc',
    'sld',
    'slw',
    'srad',
    'sradi',
    'sraw',
    'srawi',
    'srd',
    'srw',
    'stb',
    'stbcx',
    'stbdx',
    'stbepx',
    'stbu',
    'stbux',
    'stbx',
    'std',
    'stdbrx',
    'stdcx',
    'stddx',
    'stdepx',
    'stdu',
    'stdux',
    'stdx',
    'stfd',
    'stfddx',
    'stfdepx',
    'stfdu',
    'stfdux',
    'stfdx',
    'stfiwx',
    'stfs',
    'stfsu',
    'stfsux',
    'stfsx',
    'sth',
    'sthbrx',
    'sthcx',
    'sthdx',
    'sthepx',
    'sthu',
    'sthux',
    'sthx',
    'stmw',
    'stvebx',
    'stvehx',
    'stvepx',
    'stvepxl',
    'stvewx',
    'stvexbx',
    'stvexhx',
    'stvexwx',
    'stvflx',
    'stvflxl',
    'stvfrx',
    'stvfrxl',
    'stvswx',
    'stvswxl',
    'stvx',
    'stvxl',
    'stw',
    'stwbrx',
    'stwcx',
    'stwdx',
    'stwepx',
    'stwu',
    'stwux',
    'stwx',
    'subf',
    'subfb',
    'subfbss',
    'subfbu',
    'subfbus',
    'subfc',
    'subfco',
    'subfe',
    'subfeo',
    'subfh',
    'subfhss',
    'subfhu',
    'subfhus',
    'subfic',
    'subfme',
    'subfmeo',
    'subfo',
    'subfw',
    'subfwss',
    'subfwu',
    'subfwus',
    'subfze',
    'subfzeo',
    'sync',
    'td',
    'tdeq',
    'tdeqi',
    'tdge',
    'tdgei',
    'tdgt',
    'tdgti',
    'tdi',
    'tdle',
    'tdlei',
    'tdlge',
    'tdlgei',
    'tdlgt',
    'tdlgti',
    'tdlle',
    'tdllei',
    'tdllt',
    'tdllti',
    'tdlt',
    'tdlti',
    'tdne',
    'tdnei',
    'tdu',
    'tdui',
    'tlbilx',
    'tlbivax',
    'tlbre',
    'tlbsx',
    'tlbsync',
    'tlbwe',
    'trap',
    'tw',
    'tweq',
    'tweqi',
    'twge',
    'twgei',
    'twgt',
    'twgti',
    'twi',
    'twle',
    'twlei',
    'twlge',
    'twlgei',
    'twlgt',
    'twlgti',
    'twlle',
    'twllei',
    'twllt',
    'twllti',
    'twlt',
    'twlti',
    'twne',
    'twnei',
    'twui',
    'vabsdub',
    'vabsduh',
    'vabsduw',
    'vaddcuw',
    'vaddfp',
    'vaddsbs',
    'vaddshs',
    'vaddsws',
    'vaddubm',
    'vaddubs',
    'vadduhm',
    'vadduhs',
    'vadduwm',
    'vadduws',
    'vand',
    'vandc',
    'vavgsb',
    'vavgsh',
    'vavgsw',
    'vavgub',
    'vavguh',
    'vavguw',
    'vcfsx',
    'vcfux',
    'vcmpbfp',
    'vcmpeqfp',
    'vcmpequb',
    'vcmpequh',
    'vcmpequw',
    'vcmpgefp',
    'vcmpgtfp',
    'vcmpgtsb',
    'vcmpgtsh',
    'vcmpgtsw',
    'vcmpgtub',
    'vcmpgtuh',
    'vcmpgtuw',
    'vctsxs',
    'vctuxs',
    'vexptefp',
    'vlogefp',
    'vmaddfp',
    'vmaxfp',
    'vmaxsb',
    'vmaxsh',
    'vmaxsw',
    'vmaxub',
    'vmaxuh',
    'vmaxuw',
    'vmhaddshs',
    'vmhraddshs',
    'vminfp',
    'vminsb',
    'vminsh',
    'vminsw',
    'vminub',
    'vminuh',
    'vminuw',
    'vmladduhm',
    'vmrghb',
    'vmrghh',
    'vmrghw',
    'vmrglb',
    'vmrglh',
    'vmrglw',
    'vmsummbm',
    'vmsumshm',
    'vmsumshs',
    'vmsumubm',
    'vmsumuhm',
    'vmsumuhs',
    'vmulesb',
    'vmulesh',
    'vmuleub',
    'vmuleuh',
    'vmulosb',
    'vmulosh',
    'vmuloub',
    'vmulouh',
    'vnmsubfp',
    'vnor',
    'vor',
    'vperm',
    'vpkpx',
    'vpkshss',
    'vpkshus',
    'vpkswss',
    'vpkswus',
    'vpkuhum',
    'vpkuhus',
    'vpkuwum',
    'vpkuwus',
    'vrefp',
    'vrfim',
    'vrfin',
    'vrfip',
    'vrfiz',
    'vrlb',
    'vrlh',
    'vrlw',
    'vrsqrtefp',
    'vsel',
    'vsl',
    'vslb',
    'vsldoi',
    'vslh',
    'vslo',
    'vslw',
    'vspltb',
    'vsplth',
    'vspltisb',
    'vspltish',
    'vspltisw',
    'vspltw',
    'vsr',
    'vsrab',
    'vsrah',
    'vsraw',
    'vsrb',
    'vsrh',
    'vsro',
    'vsrw',
    'vsubcuw',
    'vsubfp',
    'vsubsbs',
    'vsubshs',
    'vsubsws',
    'vsububm',
    'vsububs',
    'vsubuhm',
    'vsubuhs',
    'vsubuwm',
    'vsubuws',
    'vsum2sws',
    'vsum4sbs',
    'vsum4shs',
    'vsum4ubs',
    'vsumsws',
    'vupkhpx',
    'vupkhsb',
    'vupkhsh',
    'vupklpx',
    'vupklsb',
    'vupklsh',
    'vxor',
    'wait',
    'waitrsv',
    'wrtee',
    'wrteei',
    'xor',
    'xori',
    'xoris',
)

inscounter = 0
for _mnem in mnems:
    _name = "INS_" + _mnem.upper()
    if _name in globals():
        msg = 'ERROR: cannot assign %r = %d (currently %r = %d)' % (_name, inscounter, _name, globals()[_name])
        raise Exception(msg)
    globals()[_name] = inscounter
    inscounter += 1

from . import const_gen_vle
VLE_INS_OFFSET = inscounter
for _mnem in const_gen_vle.mnems:
    _name = "INS_" + _mnem.upper()
    if _name in globals():
        if globals()[_name] >= inscounter:
            msg = 'ERROR: cannot assign %r = %d (currently %r = %d)' % (_name, inscounter, _name, globals()[_name])
            raise Exception(msg)
        else:
            # Ignore, no need to add a VLE-specific opcode
            pass
    else:
        globals()[_name] = inscounter
        inscounter += 1

IF_NONE = 0
IF_RC = 1<<8
IF_ABS = 1<<9
IF_BRANCH_LIKELY = 1<<10
IF_BRANCH_UNLIKELY = 1<<11
IF_BRANCH_PREV_TARGET = 1<<12
IF_MEM_EA = 1<<13
IF_INDEXED = 1<<14
IF_RFI = 1<<15

OF_NONE      = 0
OF_SIGNED    = 1<<1
OF_VEC_8     = 1<<2
OF_VEC_16    = 1<<3
OF_VEC_32    = 1<<4
OF_VEC_64    = 1<<5
OF_VEC_128   = 1<<6
OF_VEC_FLT   = 1<<7
OF_VEC_DBL   = 1<<8
