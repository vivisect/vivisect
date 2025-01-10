instructions = [
    ('10210208', 'evabs r1,r1'),
    ('103F0A02', 'evaddiw r1,r1,0x1f'),
    ('10211200', 'evaddw r1,r1,r2'),
    ('10221A11', 'evand r1,r2,r3'),
    ('10221A12', 'evandc r1,r2,r3'),
    ('1022020E', 'evcntlsw r1,r2'),
    ('1022020D', 'evcntlzw r1,r2'),
    ('10221A19', 'eveqv r1,r2,r3'),
    ('1022020A', 'evextsb r1,r2'),
    ('1022020B', 'evextsh r1,r2'),
    ('10220284', 'evfsabs r1,r2'),
    ('10221A80', 'evfsadd r1,r2,r3'),
    ('10228301', 'evldd r1,0x80(r2)'),
    ('10221B00', 'evlddx r1,r2,r3'),
    ('7C221E3E', 'evlddepx r1,r2,r3'),
    ('10228305', 'evldh r1,0x80(r2)'),
    ('10221B04', 'evldhx r1,r2,r3'),
    ('10228303', 'evldw r1,0x80(r2)'),
    ('10221B02', 'evldwx r1,r2,r3'),
    ('10228309', 'evlhhesplat r1,0x20(r2)'),
    ('10221B08', 'evlhhesplatx r1,r2,r3'),
    ('1022830F', 'evlhhossplat r1,0x20(r2)'),
    ('10221B0E', 'evlhhossplatx r1,r2,r3'),
    ('1022830D', 'evlhhousplat r1,0x20(r2)'),
    ('10221B0C', 'evlhhousplatx r1,r2,r3'),
    ('10228311', 'evlwhe r1,0x40(r2)'),
    ('10221B10', 'evlwhex r1,r2,r3'),
    ('10228317', 'evlwhos r1,0x40(r2)'),
    ('10221B16', 'evlwhosx r1,r2,r3'),
    ('10228315', 'evlwhou r1,0x40(r2)'),
    ('10221B14', 'evlwhoux r1,r2,r3'),
    ('1022831D', 'evlwhsplat r1,0x40(r2)'),
    ('10221B1C', 'evlwhsplatx r1,r2,r3'),
    ('10228319', 'evlwwsplat r1,0x40(r2)'),
    ('10221B18', 'evlwwsplatx r1,r2,r3'),
    ('10221A2C', 'evmergehi r1,r2,r3'),
    ('10221A2E', 'evmergehilo r1,r2,r3'),
    ('10221A2D', 'evmergelo r1,r2,r3'),
    ('10221A2F', 'evmergelohi r1,r2,r3'),
    ('102204C4', 'evmra r1,r2'),
    ('102204C9', 'evaddsmiaaw r1,r2'),
    ('102204C1', 'evaddssiaaw r1,r2'),
    ('102204C8', 'evaddumiaaw r1,r2'),
    ('102204C0', 'evaddusiaaw r1,r2'),
    ('10221D2B', 'evmhegsmfaa r1,r2,r3'),
    ('10221DAB', 'evmhegsmfan r1,r2,r3'),
    ('10221D29', 'evmhegsmiaa r1,r2,r3'),
    ('10221DA9', 'evmhegsmian r1,r2,r3'),
    ('10221D28', 'evmhegumiaa r1,r2,r3'),
    ('10221DA8', 'evmhegumian r1,r2,r3'),
    ('10221C0B', 'evmhesmf r1,r2,r3'),
    ('10221C2B', 'evmhesmfa r1,r2,r3'),
    ('10221D0B', 'evmhesmfaaw r1,r2,r3'),
    ('10221D8B', 'evmhesmfanw r1,r2,r3'),
    ('10221C09', 'evmhesmi r1,r2,r3'),
    ('10221C29', 'evmhesmia r1,r2,r3'),
    ('10221D09', 'evmhesmiaaw r1,r2,r3'),
    ('10221D89', 'evmhesmianw r1,r2,r3'),
    ('10221C08', 'evmheumi r1,r2,r3'),
    ('10221C28', 'evmheumia r1,r2,r3'),
    ('10221D08', 'evmheumiaaw r1,r2,r3'),
    ('10221D88', 'evmheumianw r1,r2,r3'),
    ('10221D2F', 'evmhogsmfaa r1,r2,r3'),
    ('10221DAF', 'evmhogsmfan r1,r2,r3'),
    ('10221D2D', 'evmhogsmiaa r1,r2,r3'),
    ('10221DAD', 'evmhogsmian r1,r2,r3'),
    ('10221D2C', 'evmhogumiaa r1,r2,r3'),
    ('10221DAC', 'evmhogumian r1,r2,r3'),
    ('10221C0F', 'evmhosmf r1,r2,r3'),
    ('10221C2F', 'evmhosmfa r1,r2,r3'),
    ('10221D0F', 'evmhosmfaaw r1,r2,r3'),
    ('10221D8F', 'evmhosmfanw r1,r2,r3'),
    ('10221C0D', 'evmhosmi r1,r2,r3'),
    ('10221C2D', 'evmhosmia r1,r2,r3'),
    ('10221D0D', 'evmhosmiaaw r1,r2,r3'),
    ('10221D8D', 'evmhosmianw r1,r2,r3'),
    ('10221C0C', 'evmhoumi r1,r2,r3'),
    ('10221C2C', 'evmhoumia r1,r2,r3'),
    ('10221D0C', 'evmhoumiaaw r1,r2,r3'),
    ('10221D8C', 'evmhoumianw r1,r2,r3'),
    ('10221C4F', 'evmwhsmf r1,r2,r3'),
    ('10221C6F', 'evmwhsmfa r1,r2,r3'),
    ('10221C4D', 'evmwhsmi r1,r2,r3'),
    ('10221C6D', 'evmwhsmia r1,r2,r3'),
    ('10221C4C', 'evmwhumi r1,r2,r3'),
    ('10221C6C', 'evmwhumia r1,r2,r3'),
    ('10221D49', 'evmwlsmiaaw r1,r2,r3'),
    ('10221DC9', 'evmwlsmianw r1,r2,r3'),
    ('10221C48', 'evmwlumi r1,r2,r3'),
    ('10221C68', 'evmwlumia r1,r2,r3'),
    ('10221D48', 'evmwlumiaaw r1,r2,r3'),
    ('10221DC8', 'evmwlumianw r1,r2,r3'),
    ('10221C5B', 'evmwsmf r1,r2,r3'),
    ('10221C7B', 'evmwsmfa r1,r2,r3'),
    ('10221D5B', 'evmwsmfaa r1,r2,r3'),
    ('10221DDB', 'evmwsmfan r1,r2,r3'),
    ('10221C59', 'evmwsmi r1,r2,r3'),
    ('10221C79', 'evmwsmia r1,r2,r3'),
    ('10221D59', 'evmwsmiaa r1,r2,r3'),
    ('10221DD9', 'evmwsmian r1,r2,r3'),
    ('10221C58', 'evmwumi r1,r2,r3'),
    ('10221C78', 'evmwumia r1,r2,r3'),
    ('10221D58', 'evmwumiaa r1,r2,r3'),
    ('10221DD8', 'evmwumian r1,r2,r3'),
    ('10221C03', 'evmhessf r1,r2,r3'),
    ('10221C23', 'evmhessfa r1,r2,r3'),
    ('10221D03', 'evmhessfaaw r1,r2,r3'),
    ('10221D83', 'evmhessfanw r1,r2,r3'),
    ('10221C07', 'evmhossf r1,r2,r3'),
    ('10221C27', 'evmhossfa r1,r2,r3'),
    ('10221D07', 'evmhossfaaw r1,r2,r3'),
    ('10221D87', 'evmhossfanw r1,r2,r3'),
    ('10221D01', 'evmhessiaaw r1,r2,r3'),
    ('10221D81', 'evmhessianw r1,r2,r3'),
    ('10221D00', 'evmheusiaaw r1,r2,r3'),
    ('10221D80', 'evmheusianw r1,r2,r3'),
    ('10221D05', 'evmhossiaaw r1,r2,r3'),
    ('10221D85', 'evmhossianw r1,r2,r3'),
    ('10221D04', 'evmhousiaaw r1,r2,r3'),
    ('10221D84', 'evmhousianw r1,r2,r3'),
    ('10221C47', 'evmwhssf r1,r2,r3'),
    ('10221C67', 'evmwhssfa r1,r2,r3'),
    ('10221C53', 'evmwssf r1,r2,r3'),
    ('10221C73', 'evmwssfa r1,r2,r3'),
    ('10221D53', 'evmwssfaa r1,r2,r3'),
    ('10221DD3', 'evmwssfan r1,r2,r3'),
    ('10221D41', 'evmwlssiaaw r1,r2,r3'),
    ('10221DC1', 'evmwlssianw r1,r2,r3'),
    ('10221D40', 'evmwlusiaaw r1,r2,r3'),
    ('10221DC0', 'evmwlusianw r1,r2,r3'),
    ('10221CC7', 'evdivwu r1,r2,r3'),
    ('10221CC6', 'evdivws r1,r2,r3'),
    ('13011234', 'evcmpeq cr6,r1,r2'),
    ('13011231', 'evcmpgts cr6,r1,r2'),
    ('13011230', 'evcmpgtu cr6,r1,r2'),
    ('13011233', 'evcmplts cr6,r1,r2'),
    ('13011232', 'evcmpltu cr6,r1,r2'),
    ('10221A1E', 'evnand r1,r2,r3'),
    ('10221A18', 'evnor r1,r2,r3'),
    ('10221A17', 'evor r1,r2,r3'),
    ('10221A16', 'evxor r1,r2,r3'),
    ('10221A1B', 'evorc r1,r2,r3'),
    ('10220209', 'evneg r1,r2'),
    ('10221A28', 'evrlw r1,r2,r3'),
    ('10221A2A', 'evrlwi r1,r2,0x3'),
    ('1022020C', 'evrndw r1,r2'),
    ('10221A7E', 'evsel r1,r2,r3,cr6'),
    ('10221A24', 'evslw r1,r2,r3'),
    ('10221A26', 'evslwi r1,r2,0x3'),
    ('10221A23', 'evsrwis r1,r2,0x3'),
    ('10221A22', 'evsrwiu r1,r2,0x3'),
    ('10221A21', 'evsrws r1,r2,r3'),
    ('10221A20', 'evsrwu r1,r2,r3'),
    ('102204CB', 'evsubfsmiaaw r1,r2'),
    ('102204C3', 'evsubfssiaaw r1,r2'),
    ('102204CA', 'evsubfumiaaw r1,r2'),
    ('102204C2', 'evsubfusiaaw r1,r2'),
    ('10221A04', 'evsubfw r1,r2,r3'),
    ('103F1206', 'evsubifw r1,0x1f,r2'),
    ('103C022B', 'evsplatfi r1,-0x4'),
    ('103C0229', 'evsplati r1,-0x4'),
    ('102C0229', 'evsplati r1,0xc'),
    ('10228321', 'evstdd r1,0x80(r2)'),
    ('10221B20', 'evstddx r1,r2,r3'),
    ('7C221F3E', 'evstddepx r1,r2,r3'),
    ('10228325', 'evstdh r1,0x80(r2)'),
    ('10228323', 'evstdw r1,0x80(r2)'),
    ('10221B24', 'evstdhx r1,r2,r3'),
    ('10221B22', 'evstdwx r1,r2,r3'),
    ('10228331', 'evstwhe r1,0x40(r2)'),
    ('10228335', 'evstwho r1,0x40(r2)'),
    ('10221B30', 'evstwhex r1,r2,r3'),
    ('10221B34', 'evstwhox r1,r2,r3'),
    ('10228339', 'evstwwe r1,0x40(r2)'),
    ('1022833D', 'evstwwo r1,0x40(r2)'),
    ('10221B38', 'evstwwex r1,r2,r3'),
    ('10221B3C', 'evstwwox r1,r2,r3'),
    ('10221A0F', 'brinc r1,r2,r3'),
]
