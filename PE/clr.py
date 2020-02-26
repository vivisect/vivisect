import enum

# https://github.com/dotnet/runtime/blob/master/src/coreclr/src/inc/corhdr.h

MAX_CLASS_NAME = MAX_PACKAGE_NAME = 1024
IMAGE_COR_EATJ_THUNK_SIZE = 32  # Size of a jump thunk reserved range.


class CLRHeaderFlags(enum.Enum):
    COMIMAGE_FLAGS_ILONLY = 0x00000001
    COMIMAGE_FLAGS_32BITREQUIRED = 0x00000002
    COMIMAGE_FLAGS_IL_LIBRARY = 0x00000004
    COMIMAGE_FLAGS_STRONGNAMESIGNED = 0x00000008
    COMIMAGE_FLAGS_NATIVE_ENTRYPOINT = 0x00000010
    COMIMAGE_FLAGS_TRACKDEBUGDATA = 0x00010000
    COMIMAGE_FLAGS_32BITPREFERRED = 0x00020000


class CLRVTableConsts(enum.Enum):
    IS_32BIT = 0x01       # V-table slots are 32-bits in size.
    IS_64BIT = 0x02       # V-table slots are 64-bits in size.
    FROM_UNMANAGED = 0x04          # If set, transition from unmanaged.
    FROM_UNMANAGED_RETAIN_APPDOMAIN = 0x08   # NEW
    CALL_MOST_DERIVED = 0x10          # Call most derived method described by


class CLRVersionFlags(enum.Enum):
    COR_VERSION_MAJOR_V2 = 2
    COR_VERSION_MAJOR = COR_VERSION_MAJOR_V2
    COR_VERSION_MINOR = 5
    COR_DELETED_NAME_LENGTH = 8
    COR_VTABLEGAP_NAME_LENGTH = 8


class CLRNativeTypeDescriptor(enum.Enum):
    NATIVE_TYPE_MAX_CB = 1
    COR_ILMETHOD_SECT_SMALL_MAX_DATASIZE = 0xFF


class CLRTypeAttrs(enum.Enum):
    VisibilityMask = 0x00000007
    NotPublic = 0x00000000  # Class is not public scope.
    Public = 0x00000001  # Class is public scope.
    NestedPublic = 0x00000002  # Class is nested with public visibility.
    NestedPrivate = 0x00000003  # Class is nested with private visibility.
    NestedFamily = 0x00000004  # Class is nested with family visibility.
    NestedAssembly = 0x00000005  # Class is nested with assembly visibility.
    # Class is nested with family and assembly visibility.
    NestedFamANDAssem = 0x00000006
    # Class is nested with family or assembly visibility.
    NestedFamORAssem = 0x00000007

    # Use this mask to retrieve class layout information
    LayoutMask = 0x00000018
    AutoLayout = 0x00000000  # Class fields are auto-laid out
    SequentialLayout = 0x00000008  # Class fields are laid out sequentially
    ExplicitLayout = 0x00000010  # Layout is supplied explicitly
    # end layout mask

    # Use this mask to retrieve class semantics information.
    ClassSemanticsMask = 0x00000020
    Class = 0x00000000  # Type is a class.
    Interface = 0x00000020  # Type is an interface.
    # end semantics mask

    # Special semantics in addition to class semantics.
    Abstract = 0x00000080  # Class is abstract
    Sealed = 0x00000100  # Class is concrete and may not be extended
    SpecialName = 0x00000400  # Class name is special.  Name describes how.

    # Implementation attributes.
    Import = 0x00001000  # Class / interface is imported
    Serializable = 0x00002000  # The class is Serializable.
    WindowsRuntime = 0x00004000  # The type is a Windows Runtime type

    # Use tdStringFormatMask to retrieve string information for native interop
    StringFormatMask = 0x00030000
    AnsiClass = 0x00000000  # LPTSTR is interpreted as ANSI in this class
    UnicodeClass = 0x00010000  # LPTSTR is interpreted as UNICODE
    AutoClass = 0x00020000  # LPTSTR is interpreted automatically
    # A non-standard encoding specified by CustomFormatMask
    CustomFormatClass = 0x00030000

    # Use this mask to retrieve non-standard encoding information for native interop.
    # The meaning of the values of these 2 bits is unspecified.
    CustomFormatMask = 0x00C00000

    # end string format mask

    # Initialize the class any time before first static field access.
    tdBeforeFieldInit = 0x00100000
    tdForwarder = 0x00200000  # This ExportedType is a type forwarder.

    # Flags reserved for runtime use.
    ReservedMask = 0x00040800
    RTSpecialName = 0x00000800  # Runtime should check name encoding.
    HasSecurity = 0x00040000  # Class has security associate with it.


class CLRMethodAttrs(enum.Enum):
    # member access mask - Use this mask to retrieve accessibility information.
    MemberAccessMask = 0x0007
    PrivateScope = 0x0000  # Member not referenceable.
    Private = 0x0001  # Accessible only by the parent type.
    FamANDAssem = 0x0002  # Accessible by sub-types only in this Assembly.
    Assem = 0x0003  # Accessibly by anyone in the Assembly.
    Family = 0x0004  # Accessible only by type and sub-types.
    # Accessibly by sub-types anywhere, plus anyone in assembly.
    FamORAssem = 0x0005
    Public = 0x0006  # Accessibly by anyone who has visibility to this scope.
    # end member access mask

    # method contract attributes.
    Static = 0x0010  # Defined on type, else per instance.
    Final = 0x0020  # Method may not be overridden.
    Virtual = 0x0040  # Method virtual.
    HideBySig = 0x0080  # Method hides by name+sig, else just by name.

    # vtable layout mask - Use this mask to retrieve vtable attributes.
    VtableLayoutMask = 0x0100
    ReuseSlot = 0x0000  # The default.
    NewSlot = 0x0100  # Method always gets a new slot in the vtable.
    # end vtable layout mask

    # method implementation attributes.
    # Overridability is the same as the visibility.
    CheckAccessOnOverride = 0x0200
    Abstract = 0x0400  # Method does not provide an implementation.
    SpecialName = 0x0800  # Method is special.  Name describes how.

    # interop attributes
    PinvokeImpl = 0x2000  # Implementation is forwarded through pinvoke.
    # Managed method exported via thunk to unmanaged code.
    UnmanagedExport = 0x0008

    # Reserved flags for runtime use only.
    ReservedMask = 0xd000
    RTSpecialName = 0x1000  # Runtime should check name encoding.
    HasSecurity = 0x4000  # Method has security associate with it.
    # Method calls another method containing security code.
    RequireSecObject = 0x8000


class CLRFieldAttrs(enum.Enum):
    # member access mask - Use this mask to retrieve accessibility information.
    FieldAccessMask = 0x0007
    PrivateScope = 0x0000  # Member not referenceable.
    Private = 0x0001  # Accessible only by the parent type.
    FamANDAssem = 0x0002  # Accessible by sub-types only in this Assembly.
    Assembly = 0x0003  # Accessibly by anyone in the Assembly.
    Family = 0x0004  # Accessible only by type and sub-types.
    # Accessibly by sub-types anywhere, plus anyone in assembly.
    FamORAssem = 0x0005
    Public = 0x0006  # Accessibly by anyone who has visibility to this scope.
    # end member access mask

    # field contract attributes.
    Static = 0x0010  # Defined on type, else per instance.
    # Field may only be initialized, not written to after init.
    InitOnly = 0x0020
    Literal = 0x0040  # Value is compile time constant.
    # Field does not have to be serialized when type is remoted.
    NotSerialized = 0x0080

    SpecialName = 0x0200  # field is special.  Name describes how.

    # interop attributes
    PinvokeImpl = 0x2000  # Implementation is forwarded through pinvoke.

    # Reserved flags for runtime use only.
    ReservedMask = 0x9500
    # Runtime(metadata internal APIs) should check name encoding.
    RTSpecialName = 0x0400
    HasFieldMarshal = 0x1000  # Field has marshalling information.
    HasDefault = 0x8000  # Field has default.
    HasFieldRVA = 0x0100  # Field has RVA.


class CLRParamAttrs(enum.Enum):
    In = 0x0001        # Param is [In]
    Out = 0x0002       # Param is [out]
    Optional = 0x0010  # Param is optional

    # Reserved flags for Runtime use only.
    ReservedMask = 0xf000
    HasDefault = 0x1000       # Param has default value.
    HasFieldMarshal = 0x2000  # Param has FieldMarshal.

    Unused = 0xcfe0


class CLRPropertyAttrs(enum.Enum):
    SpecialName = 0x0200     # property is special.  Name describes how.

    # Reserved flags for Runtime use only.
    ReservedMask = 0xf400
    # Runtime(metadata internal APIs) should check name encoding.
    RTSpecialName = 0x0400
    HasDefault = 0x1000     # Property has default
    Unused = 0xe9ff


class CLREventAttr(enum.Enum):
    SpecialName = 0x0200     # event is special.  Name describes how.

    # Reserved flags for Runtime use only.
    ReservedMask = 0x0400
    # Runtime(metadata internal APIs) should check name encoding.
    RTSpecialName = 0x0400


class CLRMethodSemanticsAttrs(enum.Enum):
    Setter = 0x0001     # Setter for property
    Getter = 0x0002     # Getter for property
    Other = 0x0004     # other method for property or event
    AddOn = 0x0008     # AddOn method for event
    RemoveOn = 0x0010     # RemoveOn method for event
    Fire = 0x0020     # Fire method for event


class CLRDeclSecurity(enum.Enum):
    ActionMask = 0x001f     # Mask allows growth of enum.
    ActionNil = 0x0000     #
    Request = 0x0001     #
    Demand = 0x0002     #
    Assert = 0x0003     #
    Deny = 0x0004     #
    PermitOnly = 0x0005     #
    LinktimeCheck = 0x0006     #
    InheritanceCheck = 0x0007     #
    RequestMinimum = 0x0008     #
    RequestOptional = 0x0009     #
    RequestRefuse = 0x000a     #
    PrejitGrant = 0x000b     # Persisted grant set at prejit time
    PrejitDenied = 0x000c     # Persisted denied set at prejit time
    NonCasDemand = 0x000d     #
    NonCasLinkDemand = 0x000e     #
    NonCasInheritance = 0x000f     #
    MaximumValue = 0x000f     # Maximum legal value


class CLRMethodImpl(enum.Enum):
    # code impl mask
    CodeTypeMask = 0x0003   # Flags about code type.
    IL = 0x0000   # Method impl is IL.
    Native = 0x0001   # Method impl is native.
    OPTIL = 0x0002   # Method impl is OPTIL
    Runtime = 0x0003   # Method impl is provided by the runtime.
    # end code impl mask

    # managed mask
    # Flags specifying whether the code is managed or unmanaged.
    ManagedMask = 0x0004
    Unmanaged = 0x0004   # Method impl is unmanaged, otherwise managed.
    Managed = 0x0000   # Method impl is managed.
    # end managed mask

    # implementation info and interop#
    # Indicates method is defined; used primarily in merge scenarios.
    ForwardRef = 0x0010
    # Indicates method sig is not to be mangled to do HRESULT conversion.
    PreserveSig = 0x0080

    InternalCall = 0x1000   # Reserved for internal use.

    Synchronized = 0x0020   # Method is single threaded through the body.
    NoInlining = 0x0008   # Method may not be inlined.
    AggressiveInlining = 0x0100   # Method should be inlined if possible.
    NoOptimization = 0x0040   # Method may not be optimized.
    # Method may contain hot code and should be aggressively optimized.
    AggressiveOptimization = 0x0200

    # These are the flags that are allowed in MethodImplAttribute's Value
    # property. This should include everything above except the code impl
    # flags (which are used for MethodImplAttribute's MethodCodeType field).
    UserMask = ManagedMask | ForwardRef | PreserveSig | InternalCall | Synchronized | \
        NoInlining | AggressiveInlining | NoOptimization | AggressiveOptimization,

    MaxMethodImplVal = 0xffff   # Range check value


class CLRPInvokeMap(enum.Enum):
    NoMangle = 0x0001   # Pinvoke is to use the member name as specified.

    # Use this mask to retrieve the CharSet information.
    CharSetMask = 0x0006
    CharSetNotSpec = 0x0000
    CharSetAnsi = 0x0002
    CharSetUnicode = 0x0004
    CharSetAuto = 0x0006

    BestFitUseAssem = 0x0000
    BestFitEnabled = 0x0010
    BestFitDisabled = 0x0020
    BestFitMask = 0x0030

    ThrowOnUnmappableCharUseAssem = 0x0000
    ThrowOnUnmappableCharEnabled = 0x1000
    ThrowOnUnmappableCharDisabled = 0x2000
    ThrowOnUnmappableCharMask = 0x3000

    # Information about target function. Not relevant for fields.
    SupportsLastError = 0x0040

    # None of the calling convention flags is relevant for fields.
    CallConvMask = 0x0700
    # Pinvoke will use native callconv appropriate to target windows platform.
    CallConvWinapi = 0x0100
    CallConvCdecl = 0x0200
    CallConvStdcall = 0x0300
    CallConvThiscall = 0x0400   # In M9, pinvoke will raise exception.
    CallConvFastcall = 0x0500

    MaxValue = 0xFFFF


class CLRAssemblyFlags(enum.Enum):
    # The assembly ref holds the full (unhashed) public key.
    PublicKey = 0x0001

    PA_None = 0x0000     # Processor Architecture unspecified
    PA_MSIL = 0x0010     # Processor Architecture: neutral (PE32)
    PA_x86 = 0x0020     # Processor Architecture: x86 (PE32)
    PA_IA64 = 0x0030     # Processor Architecture: Itanium (PE32+)
    PA_AMD64 = 0x0040     # Processor Architecture: AMD X64 (PE32+)
    PA_ARM = 0x0050     # Processor Architecture: ARM (PE32)
    PA_ARM64 = 0x0060     # Processor Architecture: ARM64 (PE32+)
    # applies to any platform but cannot run on any (e.g. reference assembly), should not have "specified" set
    PA_NoPlatform = 0x0070
    PA_Specified = 0x0080     # Propagate PA flags to AssemblyRef record
    PA_Mask = 0x0070     # Bits describing the processor architecture
    PA_FullMask = 0x00F0     # Bits describing the PA incl. Specified
    PA_Shift = 0x0004     # NOT A FLAG, shift count in PA flags <--> index conversion

    EnableJITcompileTracking = 0x8000  # From "DebuggableAttribute".
    DisableJITcompileOptimizer = 0x4000  # From "DebuggableAttribute".
    DebuggableAttributeMask = 0xc000

    # The assembly can be retargeted (at runtime) to an  assembly from a different publisher.
    Retargetable = 0x0100

    ContentType_Default = 0x0000
    ContentType_WindowsRuntime = 0x0200
    ContentType_Mask = 0x0E00  # Bits describing ContentType


class CLRManifestResourceFlags(enum.Enum):
    VisibilityMask = 0x0007
    Public = 0x0001     # The Resource is exported from the Assembly.
    Private = 0x0002     # The Resource is private to the Assembly.


class CLRFileFlags(enum.Enum):
    ContainsMetaData = 0x0000     # This is not a resource file
    # This is a resource file or other non-metadata-containing file
    ContainsNoMetaData = 0x0001


class CLRPEKind(enum.Enum):
    Not = 0x00000000       # not a PE file
    ILonly = 0x00000001       # flag IL_ONLY is set in COR header
    # flag 32BITREQUIRED is set and 32BITPREFERRED is clear in COR header
    PE32BitRequired = 0x00000002
    PE32Plus = 0x00000004     # PE32+ file (64 bit)
    PE32Unmanaged = 0x00000008     # PE32 without COR header
    # flags 32BITREQUIRED and 32BITPREFERRED are set in COR header
    PE32BitPreferred = 0x00000010


class CLRGenericParamAttr(enum.Enum):
    # Variance of type parameters, only applicable to generic parameters
    # for generic interfaces and delegates
    VarianceMask = 0x0003
    NonVariant = 0x0000
    Covariant = 0x0001
    Contravariant = 0x0002

    # Special constraints, applicable to any type parameters
    SpecialConstraintMask = 0x001C
    NoSpecialConstraint = 0x0000
    ReferenceTypeConstraint = 0x0004      # type argument must be a reference type
    # type argument must be a value type but not Nullable
    NotNullableValueTypeConstraint = 0x0008
    # type argument must have a public default constructor
    DefaultConstructorConstraint = 0x0010


class CLRSignatureElementTypes(enum.Enum):
    ELEMENT_TYPE_END = 0x00
    ELEMENT_TYPE_VOID = 0x01
    ELEMENT_TYPE_BOOLEAN = 0x02
    ELEMENT_TYPE_CHAR = 0x03
    ELEMENT_TYPE_I1 = 0x04
    ELEMENT_TYPE_U1 = 0x05
    ELEMENT_TYPE_I2 = 0x06
    ELEMENT_TYPE_U2 = 0x07
    ELEMENT_TYPE_I4 = 0x08
    ELEMENT_TYPE_U4 = 0x09
    ELEMENT_TYPE_I8 = 0x0a
    ELEMENT_TYPE_U8 = 0x0b
    ELEMENT_TYPE_R4 = 0x0c
    ELEMENT_TYPE_R8 = 0x0d
    ELEMENT_TYPE_STRING = 0x0e

    # every type above PTR will be simple type
    ELEMENT_TYPE_PTR = 0x0f     # PTR <type>
    ELEMENT_TYPE_BYREF = 0x10     # BYREF <type>

    # Please use ELEMENT_TYPE_VALUETYPE. ELEMENT_TYPE_VALUECLASS is deprecated.
    ELEMENT_TYPE_VALUETYPE = 0x11   # VALUETYPE <class Token>
    ELEMENT_TYPE_CLASS = 0x12   # CLASS <class Token>
    ELEMENT_TYPE_VAR = 0x13   # a class type variable VAR <number>
    # MDARRAY <type> <rank> <bcount> <bound1> ... <lbcount> <lb1> ...
    ELEMENT_TYPE_ARRAY = 0x14
    # GENERICINST <generic type> <argCnt> <arg1> ... <argn>
    ELEMENT_TYPE_GENERICINST = 0x15
    # TYPEDREF  (it takes no args) a typed referece to some other type
    ELEMENT_TYPE_TYPEDBYREF = 0x16

    ELEMENT_TYPE_I = 0x18   # native integer size
    ELEMENT_TYPE_U = 0x19   # native unsigned integer size
    # FNPTR <complete sig for the function including calling convention>
    ELEMENT_TYPE_FNPTR = 0x1b
    ELEMENT_TYPE_OBJECT = 0x1c   # Shortcut for System.Object
    ELEMENT_TYPE_SZARRAY = 0x1d   # Shortcut for single dimension zero lower bound array
    # SZARRAY <type>
    ELEMENT_TYPE_MVAR = 0x1e   # a method type variable MVAR <number>

    # This is only for binding
    # required C modifier : E_T_CMOD_REQD <mdTypeRef/mdTypeDef>
    ELEMENT_TYPE_CMOD_REQD = 0x1f
    # optional C modifier : E_T_CMOD_OPT <mdTypeRef/mdTypeDef>
    ELEMENT_TYPE_CMOD_OPT = 0x20

    # This is for signatures generated internally (which will not be persisted in any way).
    ELEMENT_TYPE_INTERNAL = 0x21     # INTERNAL <typehandle>

    # Note that this is the max of base type excluding modifiers
    ELEMENT_TYPE_MAX = 0x22     # first invalid element type

    ELEMENT_TYPE_MODIFIER = 0x40
    ELEMENT_TYPE_SENTINEL = 0x01 | ELEMENT_TYPE_MODIFIER  # sentinel for varargs
    ELEMENT_TYPE_PINNED = 0x05 | ELEMENT_TYPE_MODIFIER


class CLRSerializationTypes(enum.Enum):
    SERIALIZATION_TYPE_UNDEFINED = 0,
    SERIALIZATION_TYPE_BOOLEAN = CLRSignatureElementTypes.ELEMENT_TYPE_BOOLEAN
    SERIALIZATION_TYPE_CHAR = CLRSignatureElementTypes.ELEMENT_TYPE_CHAR
    SERIALIZATION_TYPE_I1 = CLRSignatureElementTypes.ELEMENT_TYPE_I1
    SERIALIZATION_TYPE_U1 = CLRSignatureElementTypes.ELEMENT_TYPE_U1
    SERIALIZATION_TYPE_I2 = CLRSignatureElementTypes.ELEMENT_TYPE_I2
    SERIALIZATION_TYPE_U2 = CLRSignatureElementTypes.ELEMENT_TYPE_U2
    SERIALIZATION_TYPE_I4 = CLRSignatureElementTypes.ELEMENT_TYPE_I4
    SERIALIZATION_TYPE_U4 = CLRSignatureElementTypes.ELEMENT_TYPE_U4
    SERIALIZATION_TYPE_I8 = CLRSignatureElementTypes.ELEMENT_TYPE_I8
    SERIALIZATION_TYPE_U8 = CLRSignatureElementTypes.ELEMENT_TYPE_U8
    SERIALIZATION_TYPE_R4 = CLRSignatureElementTypes.ELEMENT_TYPE_R4
    SERIALIZATION_TYPE_R8 = CLRSignatureElementTypes.ELEMENT_TYPE_R8
    SERIALIZATION_TYPE_STRING = CLRSignatureElementTypes.ELEMENT_TYPE_STRING
    # Shortcut for single dimension zero lower bound array
    SERIALIZATION_TYPE_SZARRAY = CLRSignatureElementTypes.ELEMENT_TYPE_SZARRAY
    SERIALIZATION_TYPE_TYPE = 0x50
    SERIALIZATION_TYPE_TAGGED_OBJECT = 0x51
    SERIALIZATION_TYPE_FIELD = 0x53
    SERIALIZATION_TYPE_PROPERTY = 0x54
    SERIALIZATION_TYPE_ENUM = 0x55


class CLRCallingConvention(enum.Enum):
    IMAGE_CEE_CS_CALLCONV_DEFAULT = 0x0

    IMAGE_CEE_CS_CALLCONV_VARARG = 0x5
    IMAGE_CEE_CS_CALLCONV_FIELD = 0x6
    IMAGE_CEE_CS_CALLCONV_LOCAL_SIG = 0x7
    IMAGE_CEE_CS_CALLCONV_PROPERTY = 0x8
    IMAGE_CEE_CS_CALLCONV_UNMGD = 0x9
    IMAGE_CEE_CS_CALLCONV_GENERICINST = 0xa  # generic method instantiation
    # used ONLY for 64bit vararg PInvoke calls
    IMAGE_CEE_CS_CALLCONV_NATIVEVARARG = 0xb
    IMAGE_CEE_CS_CALLCONV_MAX = 0xc  # first invalid calling convention

    # The high bits of the calling convention convey additional info
    IMAGE_CEE_CS_CALLCONV_MASK = 0x0f  # Calling convention is bottom 4 bits
    IMAGE_CEE_CS_CALLCONV_HASTHIS = 0x20  # Top bit indicates a 'this' parameter
    # This parameter is explicitly in the signature
    IMAGE_CEE_CS_CALLCONV_EXPLICITTHIS = 0x40
    # Generic method sig with explicit number of type arguments (precedes ordinary parameter count)
    IMAGE_CEE_CS_CALLCONV_GENERIC = 0x10
    # 0x80 is reserved for internal use


class CLRUnmanagedCallingConvention(enum.Enum):
    IMAGE_CEE_UNMANAGED_CALLCONV_C = 0x1
    IMAGE_CEE_UNMANAGED_CALLCONV_STDCALL = 0x2
    IMAGE_CEE_UNMANAGED_CALLCONV_THISCALL = 0x3
    IMAGE_CEE_UNMANAGED_CALLCONV_FASTCALL = 0x4

    IMAGE_CEE_CS_CALLCONV_C = CLRCallingConvention.IMAGE_CEE_UNMANAGED_CALLCONV_C
    IMAGE_CEE_CS_CALLCONV_STDCALL = CLRCallingConvention.IMAGE_CEE_UNMANAGED_CALLCONV_STDCALL
    IMAGE_CEE_CS_CALLCONV_THISCALL = CLRCallingConvention.IMAGE_CEE_UNMANAGED_CALLCONV_THISCALL
    IMAGE_CEE_CS_CALLCONV_FASTCALL = CLRCallingConvention.IMAGE_CEE_UNMANAGED_CALLCONV_FASTCALL


class CLRArgType(enum.Enum):
    IMAGE_CEE_CS_END = 0x0
    IMAGE_CEE_CS_VOID = 0x1
    IMAGE_CEE_CS_I4 = 0x2
    IMAGE_CEE_CS_I8 = 0x3
    IMAGE_CEE_CS_R4 = 0x4
    IMAGE_CEE_CS_R8 = 0x5
    IMAGE_CEE_CS_PTR = 0x6
    IMAGE_CEE_CS_OBJECT = 0x7
    IMAGE_CEE_CS_STRUCT4 = 0x8
    IMAGE_CEE_CS_STRUCT32 = 0x9
    IMAGE_CEE_CS_BYVALUE = 0xA


class CLRNativeTypes(enum.Enum):
    NATIVE_TYPE_END = 0x0    # DEPRECATED
    NATIVE_TYPE_VOID = 0x1    # DEPRECATED
    # (4 byte boolean value: TRUE = non-zero, FALSE = 0)
    NATIVE_TYPE_BOOLEAN = 0x2
    NATIVE_TYPE_I1 = 0x3
    NATIVE_TYPE_U1 = 0x4
    NATIVE_TYPE_I2 = 0x5
    NATIVE_TYPE_U2 = 0x6
    NATIVE_TYPE_I4 = 0x7
    NATIVE_TYPE_U4 = 0x8
    NATIVE_TYPE_I8 = 0x9
    NATIVE_TYPE_U8 = 0xa
    NATIVE_TYPE_R4 = 0xb
    NATIVE_TYPE_R8 = 0xc
    NATIVE_TYPE_SYSCHAR = 0xd    # DEPRECATED
    NATIVE_TYPE_VARIANT = 0xe    # DEPRECATED
    NATIVE_TYPE_CURRENCY = 0xf
    NATIVE_TYPE_PTR = 0x10   # DEPRECATED

    NATIVE_TYPE_DECIMAL = 0x11   # DEPRECATED
    NATIVE_TYPE_DATE = 0x12   # DEPRECATED
    NATIVE_TYPE_BSTR = 0x13   # COMINTEROP
    NATIVE_TYPE_LPSTR = 0x14
    NATIVE_TYPE_LPWSTR = 0x15
    NATIVE_TYPE_LPTSTR = 0x16
    NATIVE_TYPE_FIXEDSYSSTRING = 0x17
    NATIVE_TYPE_OBJECTREF = 0x18   # DEPRECATED
    NATIVE_TYPE_IUNKNOWN = 0x19   # COMINTEROP
    NATIVE_TYPE_IDISPATCH = 0x1a   # COMINTEROP
    NATIVE_TYPE_STRUCT = 0x1b
    NATIVE_TYPE_INTF = 0x1c   # COMINTEROP
    NATIVE_TYPE_SAFEARRAY = 0x1d   # COMINTEROP
    NATIVE_TYPE_FIXEDARRAY = 0x1e
    NATIVE_TYPE_INT = 0x1f
    NATIVE_TYPE_UINT = 0x20

    NATIVE_TYPE_NESTEDSTRUCT = 0x21  # DEPRECATED (use NATIVE_TYPE_STRUCT)

    NATIVE_TYPE_BYVALSTR = 0x22   # COMINTEROP

    NATIVE_TYPE_ANSIBSTR = 0x23   # COMINTEROP

    NATIVE_TYPE_TBSTR = 0x24   # select BSTR or ANSIBSTR depending on platform
    # COMINTEROP

    # (2-byte boolean value: TRUE = -1, FALSE = 0) COMINTEROP
    NATIVE_TYPE_VARIANTBOOL = 0x25
    NATIVE_TYPE_FUNC = 0x26

    NATIVE_TYPE_ASANY = 0x28

    NATIVE_TYPE_ARRAY = 0x2a
    NATIVE_TYPE_LPSTRUCT = 0x2b

    # Custom marshaler native type. This must be followed  by a string of the following format:
    # "Native type name/0Custom marshaler type name/0Optional cookie/0"
    # Or "{Native type GUID}/0Custom marshaler type name/0Optional cookie/0"
    NATIVE_TYPE_CUSTOMMARSHALER = 0x2c

    # This native type coupled with ELEMENT_TYPE_I4 will map to VT_HRESULT COMINTEROP
    NATIVE_TYPE_ERROR = 0x2d

    NATIVE_TYPE_IINSPECTABLE = 0x2e
    NATIVE_TYPE_HSTRING = 0x2f
    NATIVE_TYPE_LPUTF8STR = 0x30  # utf-8 string
    NATIVE_TYPE_MAX = 0x50  # first invalid element type


class CLRILMethodSect(enum.Enum):
    Reserved = 0
    EHTable = 1
    OptILTable = 2

    KindMask = 0x3F  # The mask for decoding the type code
    FatFormat = 0x40  # fat format
    MoreSects = 0x80  # there is another attribute after this one


class CLRExceptionTypes(enum.Enum):
    NONE = 0x000           # This is a typed handler
    OFFSETLEN = 0x0000     # Deprecated
    DEPRECATED = 0x0000    # Deprecated
    FILTER = 0x0001       # If this bit is on, then this EH entry is for a filter
    FINALLY = 0x0002       # This clause is a finally clause
    # Fault clause (finally that is called on exception only)
    FAULT = 0x0004
    # duplicated clause. This clause was duplicated to a funclet which was pulled out of line
    DUPLICATED = 0x0008


class CLRILMethodFlags(enum.Enum):
    InitLocals = 0x0010,           # call default constructor on all local vars
    MoreSects = 0x0008,           # there is another attribute after this one

    CompressedIL = 0x0040,           # Not used.

    # Indicates the format for the COR_ILMETHOD header
    FormatShift = 3,
    FormatMask = ((1 << FormatShift) - 1),
    TinyFormat = 0x0002,         # use this code if the code size is even
    SmallFormat = 0x0000,
    FatFormat = 0x0003,
    TinyFormat1 = 0x0006,         # use this code if the code size is odd


class CLRDuplicateChecks(enum.Enum):
    MDDupAll = 0xffffffff,
    MDDupENC = MDDupAll,
    MDNoDupChecks = 0x00000000,
    MDDupTypeDef = 0x00000001,
    MDDupInterfaceImpl = 0x00000002,
    MDDupMethodDef = 0x00000004,
    MDDupTypeRef = 0x00000008,
    MDDupMemberRef = 0x00000010,
    MDDupCustomAttribute = 0x00000020,
    MDDupParamDef = 0x00000040,
    MDDupPermission = 0x00000080,
    MDDupProperty = 0x00000100,
    MDDupEvent = 0x00000200,
    MDDupFieldDef = 0x00000400,
    MDDupSignature = 0x00000800,
    MDDupModuleRef = 0x00001000,
    MDDupTypeSpec = 0x00002000,
    MDDupImplMap = 0x00004000,
    MDDupAssemblyRef = 0x00008000,
    MDDupFile = 0x00010000,
    MDDupExportedType = 0x00020000,
    MDDupManifestResource = 0x00040000,
    MDDupGenericParam = 0x00080000,
    MDDupMethodSpec = 0x00100000,
    MDDupGenericParamConstraint = 0x00200000,
    # gap for debug junk
    MDDupAssembly = 0x10000000,

    # This is the default behavior on metadata. It will check duplicates for
    # TypeRef, MemberRef, Signature, TypeSpec and MethodSpec.
    MDDupDefault = MDNoDupChecks | MDDupTypeRef | MDDupMemberRef | MDDupSignature | MDDupTypeSpec | MDDupMethodSpec,


class CLRRefToDefCheck(enum.Enum):
    RefToDefDefault = 0x00000003
    RefToDefAll = 0xffffffff
    RefToDefNone = 0x00000000
    TypeRefToDef = 0x00000001
    MemberRefToDef = 0x00000002


class CLRNotificationForTokenMovement(enum.Enum):
    NotifyDefault = 0x0000000f
    NotifyAll = 0xffffffff
    NotifyNone = 0x00000000
    NotifyMethodDef = 0x00000001
    NotifyMemberRef = 0x00000002
    NotifyFieldDef = 0x00000004
    NotifyTypeRef = 0x00000008

    NotifyTypeDef = 0x00000010
    NotifyParamDef = 0x00000020
    NotifyInterfaceImpl = 0x00000040
    NotifyProperty = 0x00000080
    NotifyEvent = 0x00000100
    NotifySignature = 0x00000200
    NotifyTypeSpec = 0x00000400
    NotifyCustomAttribute = 0x00000800
    NotifySecurityValue = 0x00001000
    NotifyPermission = 0x00002000
    NotifyModuleRef = 0x00004000

    NotifyNameSpace = 0x00008000

    NotifyAssemblyRef = 0x01000000
    NotifyFile = 0x02000000
    NotifyExportedType = 0x04000000
    NotifyResource = 0x08000000


class CLRSetEnv(enum.Enum):
    SetENCOn = 0x00000001   # Deprecated name.
    SetENCOff = 0x00000002   # Deprecated name.
    #
    UpdateENC = 0x00000001   # ENC mode.  Tokens don't move; can be updated.
    UpdateFull = 0x00000002   # "Normal" update mode.
    # Extension mode.  Tokens don't move, adds only.
    UpdateExtension = 0x00000003
    UpdateIncremental = 0x00000004   # Incremental compilation
    UpdateDelta = 0x00000005   # If ENC on, save only deltas.
    UpdateMask = 0x00000007


class ErrorIfEmitOutOfOrder(enum.Enum):
    ErrorOutOfOrderDefault = 0x00000000   # default not to generate any error
    ErrorOutOfOrderNone = 0x00000000   # do not generate error for out of order emit
    # generate out of order emit for method, field, param, property, and event
    ErrorOutOfOrderAll = 0xffffffff
    # generate error when methods are emitted out of order
    MethodOutOfOrder = 0x00000001
    FieldOutOfOrder = 0x00000002   # generate error when fields are emitted out of order
    ParamOutOfOrder = 0x00000004   # generate error when params are emitted out of order
    # generate error when properties are emitted out of order
    PropertyOutOfOrder = 0x00000008
    EventOutOfOrder = 0x00000010


class CLRImportOptions(enum.Enum):
    ImportOptionDefault = 0x00000000       # default to skip over deleted records
    ImportOptionAll = 0xFFFFFFFF       # Enumerate everything
    # all of the typedefs including the deleted typedef
    ImportOptionAllTypeDefs = 0x00000001
    # all of the methoddefs including the deleted ones
    ImportOptionAllMethodDefs = 0x00000002
    # all of the fielddefs including the deleted ones
    ImportOptionAllFieldDefs = 0x00000004
    # all of the properties including the deleted ones
    ImportOptionAllProperties = 0x00000008
    # all of the events including the deleted ones
    ImportOptionAllEvents = 0x00000010
    # all of the custom attributes including the deleted ones
    ImportOptionAllCustomAttributes = 0x00000020
    # all of the ExportedTypes including the deleted ones
    ImportOptionAllExportedTypes = 0x00000040


class CLRThreadSafetyOptions(enum.Enum):
    ThreadSafetyDefault = 0x00000000
    ThreadSafetyOff = 0x00000000
    ThreadSafetyOn = 0x00000001


class CLRLinkerOptions(enum.Enum):
    Assembly = 0x00000000
    NetModule = 0x00000001


class CLRMergeFlags(enum.Enum):
    MergeFlagsNone = 0
    MergeManifest = 0x00000001
    DropMemberRefCAs = 0x00000002
    NoDupCheck = 0x00000004
    MergeExportedTypes = 0x00000008


class CLRLocalRefPreservation(enum.Enum):
    PreserveLocalRefsNone = 0x00000000
    PreserveLocalTypeRef = 0x00000001
    PreserveLocalMemberRef = 0x00000002


class CLRCoreTokenType(enum.Enum):
    mdtModule = 0x00000000
    mdtTypeRef = 0x01000000
    mdtTypeDef = 0x02000000
    mdtFieldDef = 0x04000000
    mdtMethodDef = 0x06000000
    mdtParamDef = 0x08000000
    mdtInterfaceImpl = 0x09000000
    mdtMemberRef = 0x0a000000
    mdtCustomAttribute = 0x0c000000
    mdtPermission = 0x0e000000
    mdtSignature = 0x11000000
    mdtEvent = 0x14000000
    mdtProperty = 0x17000000
    mdtMethodImpl = 0x19000000
    mdtModuleRef = 0x1a000000
    mdtTypeSpec = 0x1b000000
    mdtAssembly = 0x20000000
    mdtAssemblyRef = 0x23000000
    mdtFile = 0x26000000
    mdtExportedType = 0x27000000
    mdtManifestResource = 0x28000000
    mdtGenericParam = 0x2a000000
    mdtMethodSpec = 0x2b000000
    mdtGenericParamConstraint = 0x2c000000
    mdtString = 0x70000000
    mdtName = 0x71000000
    # Leave this on the high end value. This does not correspond to metadata table
    mdtBaseType = 0x72000000


class CLRCoreOpenFlags(enum.Enum):
    Read = 0x00000000,     # Open scope for read
    Write = 0x00000001,     # Open scope for write.
    ReadWriteMask = 0x00000001,     # Mask for read/write bit.

    # Open scope with memory. Ask metadata to maintain its own copy of memory.
    CopyMemory = 0x00000002,

    # Open scope for read. Will be unable to QI for a IMetadataEmit* interface
    ReadOnly = 0x00000010,
    # The memory was allocated with CoTaskMemAlloc and will be freed by the metadata
    TakeOwnership = 0x00000020,

    # These are obsolete and are ignored. (and are comented out in the OG source)
    # ofCacheImage     =   0x00000004,     # EE maps but does not do relocations or verify image
    # ofManifestMetadata = 0x00000008,     # Open scope on ngen image, return the manifest metadata instead of the IL metadata
    NoTypeLib = 0x00000080,     # Don't OpenScope on a typelib.
    # Disable automatic transforms of .winmd files.
    NoTransform = 0x00001000,

    # Internal bits
    Reserved1 = 0x00000100,     # Reserved for internal use.
    Reserved2 = 0x00000200,     # Reserved for internal use.
    Reserved3 = 0x00000400,     # Reserved for internal use.
    Reserved = 0xffffef40      # All the reserved bits.


class CLRCoreAttrTargets(enum.Enum):
    catAssembly = 0x0001
    catModule = 0x0002
    catClass = 0x0004
    catStruct = 0x0008
    catEnum = 0x0010
    catConstructor = 0x0020
    catMethod = 0x0040
    catProperty = 0x0080
    catField = 0x0100
    catEvent = 0x0200
    catInterface = 0x0400
    catParameter = 0x0800
    catDelegate = 0x1000
    catGenericParameter = 0x4000

    catAll = catAssembly | catModule | catClass | catStruct | catEnum | catConstructor | catMethod | catProperty | catField | catEvent | catInterface | catParameter | catDelegate | catGenericParameter,
    catClassMembers = catClass | catStruct | catEnum | catConstructor | catMethod | catProperty | catField | catEvent | catDelegate | catInterface,


class CLRNgenHints(enum.Enum):
    NGenDefault             = 0x0000  # No preference specified
    NGenEager               = 0x0001  # NGen at install time
    NGenLazy                = 0x0002  # NGen after install time
    NGenNever               = 0x0003  # Assembly should not be ngened


class CLRLoadHints(enum.Enum):
    LoadDefault             = 0x0000  # No preference specified
    LoadAlways              = 0x0001  # Dependency is always loaded
    LoadSometimes           = 0x0002  # Dependency is sometimes loaded
    LoadNever               = 0x0003  # Dependency is never loaded


class CLRCoreSaveSize(enum.Enum):
    cssAccurate             = 0x0000  # Find exact save size, accurate but slower.
    cssQuick                = 0x0001  # Estimate save size, may pad estimate, but faster.
    cssDiscardTransientCAs  = 0x0002  # remove all of the CAs of discardable types
