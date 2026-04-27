import { type Address, zeroAddress } from "viem";

import { ARBITRUM,CELO,ARBITRUM_SEPOLIA, AVALANCHE, AVALANCHE_FUJI, BOTANIX, ContractsChainId } from "./chains";

export const CONTRACTS = {
  [CELO]: {
    // Synthetics
    DataStore: '0x2808EFda9b6c464208d14aF22A793AD1725D5836', //1
    EventEmitter: '0x6db23e3B53958c449b7DF6D639A1333ca99EB937', //1
    ExchangeRouter: '0x20095BB2Fe7C8d25D15d6e5985b29755Ef57EecE', //1
    DepositVault: '0x2690A62C0c19F91f0d59A104955322451F951F90', //1
    WithdrawalVault: '0x0336b6eDa5F1889092005ebb78648c2a02d406e3', //1
    OrderVault: '0x3153298B530048dD4E079cB9156d9A2DFdA9F0Dc', //1
    SyntheticsReader: '0x357A2044aD1DfE8c93e7dcf352DD4785b1C6CD93', //1
    SyntheticsRouter: '0x5C1e75b8425F9B0de50F8aA5846189fe8676e463', //1
    ChainlinkPriceFeedProvider: '0x3f1932ba80878364575d91B822272044E76C87e3', //1
    ReferralStorage: '0x2128E99291A77e4De5ce47Db8527B6121C86eF6A', //1

    // External
    ExternalHandler: '0xDe7b4FD689214653E5aF59Be8fB824DAE09E43cd', //1
    Multicall: '0x36C82Afc5c7Fc7D29bf84C0DF383534B2B46DB18', //1
    NATIVE_TOKEN: '0x471EcE3750Da237f93B8E339c536989b8978a438', //1
  
        //ClaimHandler: "",
    GlvReader: "0xF03b0A5AE2D7cEA9FB060E82b9CC8E47F176dF5C",
    GlvRouter: "0x4E9D0Ad492208A60d2e7751a8c3B9A1eAe5400Fc",
    GlvVault: "0x3f4De047E510AAd0fBDFB3A131fFfEa6f5548C08",
    ShiftVault: "0xb30e7A63B852DEA3443c1187d323e65c3e76711F",
  
    GelatoRelayRouter: "0x51c2A9DB0298bBA5cFe5061d511D030D1683935C",
    SubaccountRouter: "0x2cA7857ec0dCcC688052d4d5A4269F3E4e342B45",
    SubaccountGelatoRelayRouter: "0x1B3b07548ACf5B20c0BF4F62a59aa493a22D3fB0",
  
    //LayerZeroEndpoint: "",
    //ArbitrumNodeInterface: "",
    //GelatoRelayAddress: "",

  },
  [ARBITRUM]: {
    // V1
    Vault: "0x489ee077994B6658eAfA855C308275EAd8097C4A",
    VaultReader: "0xfebB9f4CAC4cD523598fE1C5771181440143F24A",
    Reader: "0x2b43c90D1B727cEe1Df34925bcd5Ace52Ec37694",
    GlpManager: "0x3963FfC9dff443c2A94f21b129D429891E32ec18",
    RewardRouter: "0x5E4766F932ce00aA4a1A82d3Da85adf15C5694A1",
    GlpRewardRouter: "0xB95DB5B167D75e6d04227CfFFA61069348d271F5",
    RewardReader: "0x8BFb8e82Ee4569aee78D03235ff465Bd436D40E0",
    GovToken: "0x2A29D3a792000750807cc401806d6fd539928481",
    NATIVE_TOKEN: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
    GLP: "0x4277f8F2c384827B5273592FF7CeBd9f2C1ac258",
    GMX: "0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a",
    ES_GMX: "0xf42Ae1D54fd613C9bb14810b0588FaAa09a426cA",
    BN_GMX: "0x35247165119B69A40edD5304969560D0ef486921",
    USDG: "0x45096e7aA921f27590f8F19e457794EB09678141",
    ES_GMX_IOU: "0x6260101218eC4cCfFF1b778936C6f2400f95A954",
    StakedGmxTracker: "0x908C4D94D34924765f1eDc22A1DD098397c59dD4",
    BonusGmxTracker: "0x4d268a7d4C16ceB5a606c173Bd974984343fea13",
    FeeGmxTracker: "0xd2D1162512F927a7e282Ef43a362659E4F2a728F",
    StakedGlpTracker: "0x1aDDD80E6039594eE970E5872D247bf0414C8903",
    FeeGlpTracker: "0x4e971a87900b931fF39d1Aad67697F49835400b6",
    ExtendedGmxTracker: "0x0755D33e45eD2B874c9ebF5B279023c8Bd1e5E93",

    StakedGmxDistributor: "0x23208B91A98c7C1CD9FE63085BFf68311494F193",
    StakedGlpDistributor: "0x60519b48ec4183a61ca2B8e37869E675FD203b34",

    GmxVester: "0x199070DDfd1CFb69173aa2F7e20906F26B363004",
    GlpVester: "0xA75287d2f8b217273E7FCD7E86eF07D33972042E",
    AffiliateVester: "0x7c100c0F55A15221A4c1C5a25Db8C98A81df49B2",

    PositionRouter: "0xb87a436B93fFE9D75c5cFA7bAcFff96430b09868",

    UniswapGmxEthPool: "0x80A9ae39310abf666A87C743d6ebBD0E8C42158E",
    ReferralStorage: "0xe6fab3f0c7199b0d34d7fbe83394fc0e0d06e99d",
    Timelock: "0xaa50bD556CE0Fe61D4A57718BA43177a3aB6A597",

    DataStore: "0x755273464bF4917702Ff45Ae13788F4493c34459",
    EventEmitter: "0x801C8fc51846D6EcD5EFd9C196732A8c30ddB503",
    SubaccountRouter: "0x95cEEd896f3f8C2767Bf774e91fEDf727e94A600",
    ExchangeRouter: "0x909babe2dFBa13f9DC9655A19003Dbe8e9124d5b",
    DepositVault: "0xf7f2a4751f7e26C91C0726EFDDbaA414dD09BCef",
    WithdrawalVault: "0x296AC5d663Abb2551ddc7FD51c54C5F2BB03fDB3",
    OrderVault: "0xCFEd939845c05922B027b2BBCE06aFF5E50bc380",
    ShiftVault: "0x16Ed2576BaC6c8A9c07995175C73c2dd4cb4406a",
    SyntheticsReader: "0xe616B555f322b710FA33eBcd5895b671c6EF2FCe",
    SyntheticsRouter: "0x4c73F36B1851e2160155D17E1241AF386dc5e1A7",

    GlvReader: "0x4C1B81dE49D28ce4235C4c1faC50c39919C739c1",
    GlvRouter: "0xf8C1aC0acC6A44C20D44d5CD543774120Dd4B9aF",
    GlvVault: "0x677994626ebEa2CE8e9Ce194FEf77559fFc1Ec2C",

    GelatoRelayRouter: "0x096059301e07569dF4019050Ab5a89d3436e312E",
    SubaccountGelatoRelayRouter: "0x6113f628c4F2873A88AE74D982D5a84bF1E32ae6",

    MultichainClaimsRouter: "0x2A7244EE5373D2F161cE99F0D144c12860D651Af",
    MultichainGlvRouter: "0xFdaFa6fbd4B480017FD37205Cb3A24AE93823956",
    MultichainGmRouter: "0xF53e30CE07f148fdE6e531Be7dC0b6ad670E8C6e",
    MultichainOrderRouter: "0x3c796504d47013Ea0552CCa57373B59DF03D34a0",
    MultichainSubaccountRouter: "0x99CD306B777C5aAb842bA65e4f7FF0554ECDe808",
    MultichainTransferRouter: "0xC1D1354A948bf717d6d873e5c0bE614359AF954D",
    MultichainVault: "0xCeaadFAf6A8C489B250e407987877c5fDfcDBE6E",
    LayerZeroProvider: "0x7129Ea01F0826c705d6F7ab01Cf3C06bb83E9397",

    ChainlinkPriceFeedProvider: "0x25386Ad45c7BE8E97afb9a531Dbb2B24d2C83cCf",
    ClaimHandler: "0x28f1F4AA95F49FAB62464536A269437B13d48976",
    // External
    ExternalHandler: "0xf52c4e03ec54bf8CF6853Fe4B936aa0E19eb9158",
    OpenOceanRouter: "0x6352a56caadC4F1E25CD6c75970Fa768A3304e64",
    Multicall: "0xe79118d6D92a4b23369ba356C90b9A7ABf1CB961",
    ArbitrumNodeInterface: "0x00000000000000000000000000000000000000C8",
    LayerZeroEndpoint: "0x1a44076050125825900e736c501f859c50fE728c",
    GelatoRelayAddress: "0xaBcC9b596420A9E9172FD5938620E265a0f9Df92",
  },
  [AVALANCHE]: {
    // V1
    Vault: "0x9ab2De34A33fB459b538c43f251eB825645e8595",
    VaultReader: "0x66eC8fc33A26feAEAe156afA3Cb46923651F6f0D",
    Reader: "0x2eFEE1950ededC65De687b40Fd30a7B5f4544aBd",
    GlpManager: "0xD152c7F25db7F4B95b7658323c5F33d176818EE4",
    RewardRouter: "0x091eD806490Cc58Fd514441499e58984cCce0630",
    GlpRewardRouter: "0xB70B91CE0771d3f4c81D87660f71Da31d48eB3B3",
    RewardReader: "0x04Fc11Bd28763872d143637a7c768bD96E44c1b6",
    GovToken: "0x0ff183E29f1924ad10475506D7722169010CecCb",
    NATIVE_TOKEN: "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
    GLP: "0x01234181085565ed162a948b6a5e88758CD7c7b8",
    GMX: "0x62edc0692BD897D2295872a9FFCac5425011c661",
    ES_GMX: "0xFf1489227BbAAC61a9209A08929E4c2a526DdD17",
    BN_GMX: "0x8087a341D32D445d9aC8aCc9c14F5781E04A26d2",
    USDG: "0xc0253c3cC6aa5Ab407b5795a04c28fB063273894",
    ES_GMX_IOU: "0x6260101218eC4cCfFF1b778936C6f2400f95A954", // placeholder address

    StakedGmxTracker: "0x2bD10f8E93B3669b6d42E74eEedC65dd1B0a1342",
    BonusGmxTracker: "0x908C4D94D34924765f1eDc22A1DD098397c59dD4",
    FeeGmxTracker: "0x4d268a7d4C16ceB5a606c173Bd974984343fea13",
    StakedGlpTracker: "0x9e295B5B976a184B14aD8cd72413aD846C299660",
    FeeGlpTracker: "0xd2D1162512F927a7e282Ef43a362659E4F2a728F",
    ExtendedGmxTracker: "0xB0D12Bf95CC1341d6C845C978daaf36F70b5910d",

    StakedGmxDistributor: "0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a",
    StakedGlpDistributor: "0xDd593Cf40734199afc9207eBe9ffF23dA4Bf7720",

    GmxVester: "0x472361d3cA5F49c8E633FB50385BfaD1e018b445",
    GlpVester: "0x62331A7Bd1dfB3A7642B7db50B5509E57CA3154A",
    AffiliateVester: "0x754eC029EF9926184b4CFDeA7756FbBAE7f326f7",

    PositionRouter: "0xffF6D276Bc37c61A23f06410Dce4A400f66420f8",

    TraderJoeGmxAvaxPool: "0x0c91a070f862666bbcce281346be45766d874d98",
    ReferralStorage: "0x827ed045002ecdabeb6e2b0d1604cf5fc3d322f8",
    Timelock: "0x8A68a039D555599Fd745f9343e8dE20C9eaFca75",

    // Synthetics
    DataStore: "0x2F0b22339414ADeD7D5F06f9D604c7fF5b2fe3f6",
    EventEmitter: "0xDb17B211c34240B014ab6d61d4A31FA0C0e20c26",
    SubaccountRouter: "0x88a5c6D94634Abd7745f5348e5D8C42868ed4AC3",
    ExchangeRouter: "0xF0864BE1C39C0AB28a8f1918BC8321beF8F7C317",
    DepositVault: "0x90c670825d0C62ede1c5ee9571d6d9a17A722DFF",
    WithdrawalVault: "0xf5F30B10141E1F63FC11eD772931A8294a591996",
    OrderVault: "0xD3D60D22d415aD43b7e64b510D86A30f19B1B12C",
    ShiftVault: "0x7fC46CCb386e9bbBFB49A2639002734C3Ec52b39",
    SyntheticsReader: "0x1EC018d2b6ACCA20a0bEDb86450b7E27D1D8355B",
    SyntheticsRouter: "0x820F5FfC5b525cD4d88Cd91aCf2c28F16530Cc68",

    GlvReader: "0x12Ac77003B3D11b0853d1FD12E5AF22a9060eC4b",
    GlvRouter: "0x4729D9f61c0159F5e02D2C2e5937B3225e55442C",
    GlvVault: "0x527FB0bCfF63C47761039bB386cFE181A92a4701",

    GelatoRelayRouter: "0xa61f92ab63cc5C3d60574d40A6e73861c37aaC95",
    SubaccountGelatoRelayRouter: "0x58b09FD12863218F2ca156808C2Ae48aaCD0c072",

    MultichainClaimsRouter: "0x9080f8A35Da53F4200a68533FB1dC1cA05357bDB",
    MultichainGlvRouter: "0x2A7244EE5373D2F161cE99F0D144c12860D651Af",
    MultichainGmRouter: "0x10Fa5Bd343373101654E896B43Ca38Fd8f3789F9",
    MultichainOrderRouter: "0x99CD306B777C5aAb842bA65e4f7FF0554ECDe808",
    MultichainSubaccountRouter: "0xB36a4c6cDeDea3f31b3d16F33553F93b96b178F4",
    MultichainTransferRouter: "0x8c6e20A2211D1b70cD7c0789EcE44fDB19567621",
    MultichainVault: "0x6D5F3c723002847B009D07Fe8e17d6958F153E4e",
    LayerZeroProvider: "0xA1D94802EcD642051B677dBF37c8E78ce6dd3784",

    ChainlinkPriceFeedProvider: "0x05d97cee050bfb81FB3EaD4A9368584F8e72C88e",
    ClaimHandler: "0x7FfedCAC2eCb2C29dDc027B60D6F8107295Ff2eA",

    // External
    ExternalHandler: "0xD149573a098223a9185433290a5A5CDbFa54a8A9",
    OpenOceanRouter: "0x6352a56caadC4F1E25CD6c75970Fa768A3304e64",
    Multicall: "0x50474CAe810B316c294111807F94F9f48527e7F8",
    ArbitrumNodeInterface: zeroAddress,
    LayerZeroEndpoint: "0x1a44076050125825900e736c501f859c50fE728c",
    GelatoRelayAddress: "0xaBcC9b596420A9E9172FD5938620E265a0f9Df92",
  },
  [BOTANIX]: {
    // Synthetics
    DataStore: "0xA23B81a89Ab9D7D89fF8fc1b5d8508fB75Cc094d",
    EventEmitter: "0xAf2E131d483cedE068e21a9228aD91E623a989C2",
    SubaccountRouter: "0x11E590f6092D557bF71BaDEd50D81521674F8275",
    ExchangeRouter: "0x72fa3978E2E330C7B2debc23CB676A3ae63333F6",
    DepositVault: "0x4D12C3D3e750e051e87a2F3f7750fBd94767742c",
    WithdrawalVault: "0x46BAeAEdbF90Ce46310173A04942e2B3B781Bf0e",
    OrderVault: "0xe52B3700D17B45dE9de7205DEe4685B4B9EC612D",
    ShiftVault: "0xa7EE2737249e0099906cB079BCEe85f0bbd837d4",

    SyntheticsReader: "0xa254B60cbB85a92F6151B10E1233639F601f2F0F",
    SyntheticsRouter: "0x3d472afcd66F954Fe4909EEcDd5c940e9a99290c",

    GlvReader: "0x490d660A21fB75701b7781E191cB888D1FE38315",
    GlvRouter: "0x348Eca94e7c6F35430aF1cAccE27C29E9Bef9ae3",
    GlvVault: "0xd336087512BeF8Df32AF605b492f452Fd6436CD8",

    GelatoRelayRouter: "0x7f8eF83C92B48a4B5B954A24D98a6cD0Ed4D160a",
    SubaccountGelatoRelayRouter: "0xfbb9C41046E27405224a911f44602C3667f9D8f6",

    MultichainClaimsRouter: "0x790Ee987b9B253374d700b07F16347a7d4C4ff2e",
    MultichainGlvRouter: "0xEE027373517a6D96Fe62f70E9A0A395cB5a39Eee",
    MultichainGmRouter: "0x4ef8394CD5DD7E3EE6D30824689eF461783a3360",
    MultichainOrderRouter: "0x5c5DBbcDf420B5d81d4FfDBa5b26Eb24E6E60d52",
    MultichainSubaccountRouter: "0xd3B6E962f135634C43415d57A28E688Fb4f15A58",
    MultichainTransferRouter: "0x901f26a57edCe65Ef3FBcCD260433De9B2279852",
    MultichainVault: "0x9a535f9343434D96c4a39fF1d90cC685A4F6Fb20",
    LayerZeroProvider: "0x61af99b07995cb7Ee8c2FACF6D8fb6042FeAA0d9",

    ChainlinkPriceFeedProvider: "0xDc613305e9267f0770072dEaB8c03162e0554b2d",
    ClaimHandler: "0x3ca0f3ad78a9d0b2a0c060fe86d1141118a285c4",

    // External
    ExternalHandler: "0x36b906eA6AE7c74aeEE8cDE66D01B3f1f8843872",
    OpenOceanRouter: zeroAddress,
    Multicall: "0x4BaA24f93a657f0c1b4A0Ffc72B91011E35cA46b",
    LayerZeroEndpoint: "0x6F475642a6e85809B1c36Fa62763669b1b48DD5B",
    ArbitrumNodeInterface: zeroAddress,
    GelatoRelayAddress: "0x61aCe8fBA7B80AEf8ED67f37CB60bE00180872aD",

    Vault: zeroAddress,
    Reader: zeroAddress,
    PositionRouter: zeroAddress,
    ReferralStorage: zeroAddress,
    VaultReader: zeroAddress,
    GlpManager: zeroAddress,
    RewardRouter: zeroAddress,
    RewardReader: zeroAddress,
    GlpRewardRouter: zeroAddress,
    StakedGmxTracker: zeroAddress,
    FeeGmxTracker: zeroAddress,
    GLP: zeroAddress,
    GMX: zeroAddress,
    ES_GMX: zeroAddress,
    BN_GMX: zeroAddress,
    USDG: zeroAddress,
    BonusGmxTracker: zeroAddress,
    StakedGlpTracker: zeroAddress,
    FeeGlpTracker: zeroAddress,
    ExtendedGmxTracker: zeroAddress,
    StakedGmxDistributor: zeroAddress,
    StakedGlpDistributor: zeroAddress,
    GmxVester: zeroAddress,
    GlpVester: zeroAddress,
    AffiliateVester: zeroAddress,
    Router: zeroAddress,
    GovToken: zeroAddress,
    ES_GMX_IOU: zeroAddress,
    OrderBook: zeroAddress,

    UniswapGmxEthPool: zeroAddress,

    // botanix specific
    NATIVE_TOKEN: "0x0D2437F93Fed6EA64Ef01cCde385FB1263910C56",
    StBTC: "0xF4586028FFdA7Eca636864F80f8a3f2589E33795",
    PBTC: "0x0D2437F93Fed6EA64Ef01cCde385FB1263910C56",
  },

  [AVALANCHE_FUJI]: {
    // V1
    Vault: zeroAddress,
    Router: zeroAddress,
    VaultReader: zeroAddress,
    Reader: zeroAddress,
    GlpManager: zeroAddress,
    RewardRouter: zeroAddress,
    RewardReader: zeroAddress,
    GlpRewardRouter: zeroAddress,
    NATIVE_TOKEN: "0x1D308089a2D1Ced3f1Ce36B1FcaF815b07217be3",
    GLP: zeroAddress,
    GMX: zeroAddress,
    ES_GMX: zeroAddress,
    BN_GMX: zeroAddress,
    USDG: zeroAddress,
    ES_GMX_IOU: zeroAddress,

    StakedGmxTracker: zeroAddress,
    BonusGmxTracker: zeroAddress,
    FeeGmxTracker: zeroAddress,
    StakedGlpTracker: zeroAddress,
    FeeGlpTracker: zeroAddress,
    ExtendedGmxTracker: zeroAddress,

    StakedGmxDistributor: zeroAddress,
    StakedGlpDistributor: zeroAddress,

    GmxVester: zeroAddress,
    GlpVester: zeroAddress,
    AffiliateVester: zeroAddress,

    PositionRouter: zeroAddress,

    TraderJoeGmxAvaxPool: zeroAddress,
    ReferralStorage: "0x192e82A18a4ab446dD9968f055431b60640B155D",

    // Synthetics
    DataStore: "0xEA1BFb4Ea9A412dCCd63454AbC127431eBB0F0d4",
    EventEmitter: "0xc67D98AC5803aFD776958622CeEE332A0B2CabB9",
    ExchangeRouter: "0x0a458C96Ac0B2a130DA4BdF1aAdD4cb7Be036d11",
    SubaccountRouter: "0xD5EE3ECAF5754CE5Ff74847d0caf094EBB12ed5e",
    DepositVault: "0x2964d242233036C8BDC1ADC795bB4DeA6fb929f2",
    WithdrawalVault: "0x74d49B6A630Bf519bDb6E4efc4354C420418A6A2",
    OrderVault: "0x25D23e8E655727F2687CC808BB9589525A6F599B",
    ShiftVault: "0x257D0EA0B040E2Cd1D456fB4C66d7814102aD346",
    SyntheticsReader: "0xf82Cc6EB57F8FF86bc5c5e90B8BA83DbBFB517eE",
    SyntheticsRouter: "0x5e7d61e4C52123ADF651961e4833aCc349b61491",
    Timelock: zeroAddress,

    GlvReader: "0xdeaC9ea3c72C102f2a9654b8E1A14Ef86Cdd3146",
    GlvRouter: "0x6B6595389A0196F882C0f66CB1F401f1D24afEdC",
    GlvVault: "0x76f93b5240DF811a3fc32bEDd58daA5784e46C96",

    GelatoRelayRouter: "0xC2917611f422b1624D7316375690B532c149F54b",
    SubaccountGelatoRelayRouter: "0x9022ADce7c964852475aB0de801932BaDEB0C765",

    MultichainClaimsRouter: "0xa080c3E026467E1fa6E76D29A057Bf1261a4ec86",
    MultichainGlvRouter: "0x5060A75868ca21A54C650a70E96fa92405831b15",
    MultichainGmRouter: "0xe32632F65198eF3080ccDe22A6d23819203dBc42",
    MultichainOrderRouter: "0x6169DD9Bc75B1d4B7138109Abe58f5645BA6B8fE",
    MultichainSubaccountRouter: "0xa51181CC37D23d3a4b4B263D2B54e1F34B834432",
    MultichainTransferRouter: "0x0bD6966B894D9704Ce540babcd425C93d2BD549C",
    MultichainVault: "0xFd86A5d9D6dF6f0cB6B0e6A18Bea7CB07Ada4F79",
    LayerZeroProvider: "0xdaa9194bFD143Af71A8d2cFc8F2c0643094a77C5",

    ChainlinkPriceFeedProvider: "0x2e149AbC99cDC98FB0207d6F184DC323CEBB955B",
    ClaimHandler: "0x01D68cf13B8f67b041b8D565931e1370774cCeBd",

    // External
    OpenOceanRouter: zeroAddress,
    ExternalHandler: "0x0d9F90c66C392c4d0e70EE0d399c43729B942512",
    Multicall: "0x966D1F5c54a714C6443205F0Ec49eEF81F10fdfD",
    ArbitrumNodeInterface: zeroAddress,
    LayerZeroEndpoint: "0x6EDCE65403992e310A62460808c4b910D972f10f",
  },

  [ARBITRUM_SEPOLIA]: {
  // Synthetics
  DataStore: "0x6Df1a53D47C2527705af0bC27371aEDeE4b8B081",//1
  EventEmitter: "0xE172d3CfBce9Cf4F354a82a24031eBAC0A894FFa",//1
  ExchangeRouter: "0xAFB5F02871E288c2f3B5E4A3b9A7f6F9C5a5f42E", //1
  SubaccountRouter: "0x7d4dD31B32F6Ae51893B6cffCAb15E75eA30D69b",
  DepositVault: "0xd9fc419dCd241c25aDD7828E5Dda4D004c19b090",//1
  WithdrawalVault: "0x3C7B36902f1A3683d944e774c0A7dfB4cd9013d7", //1
  OrderVault: "0xF75B4A82bF373Ac4eFc9b4075800DF9a7ecBA3Ea",//1
  ShiftVault: "0xCB883210CEeFc113F66e6CC41f934C7EE47Ad4F5",//1
  SyntheticsReader: "0xc1D4dEBF516C5aEF1288798e9A18c98ed0618210",
  SyntheticsRouter: "0x2023454F4cE236D770b9104Eaf92FCeAD292e808",

  GlvReader: "0x4843D570c726cFb44574c1769f721a49c7e9c350",
  GlvRouter: "0x7F8af0741e8925C132E84147762902EBBc485d11",
  GlvVault: "0x40bD50de0977c68ecB958ED4A065E14E1091ce64",

  GelatoRelayRouter: "0x44904137A4d8734a5AB13B32083FFd6B93664491",
  SubaccountGelatoRelayRouter: "0x209E4408D68EE049957dBba7Ac62177f10ee00ab",

  MultichainClaimsRouter: "0xe06534c26c90AE8c3241BC90dDB69d4Af438f17f",
  MultichainGlvRouter: "0x29b9a624a29327b1c76317bfF08373281c582B79",
  MultichainGmRouter: "0x9868Ab73D1cB4DcEEd74e5eB9f86346C935488F3",
  MultichainOrderRouter: "0x2B977188b3Bf8fbCa2Ca5D6e00DC8542b7690C9E",
  MultichainSubaccountRouter: "0xf8fbE9411f90618B3c68A8826555Ab54dE090ED7",
  MultichainTransferRouter: "0xeCfcA6af46B9d20793f82b28bc749dfFC6DEE535",
  MultichainVault: "0xCd46EF5ed7d08B345c47b5a193A719861Aa2CD91",
  LayerZeroProvider: "0x3f85e237E950A7FB7cfb6DD4C262353A82588d51",

  ChainlinkPriceFeedProvider: "0x4a2102E95E555DAe68dF68c4ec8A1F40b373B7b5",//1
  ReferralStorage: "0x0555f6a98F008c5e5D7374c9679B10A07d252A87",//1
  ClaimHandler: "0x96FE82b9C6FE46af537cE465B3befBD7b076C982",

  // External
  Multicall: "0xD84793ae65842fFac5C20Ab8eaBD699ea1FC79F3",
  NATIVE_TOKEN: "0x980B62Da83eFf3D4576C647993b0c1D7faf17c73",
  LayerZeroEndpoint: "0x6EDCE65403992e310A62460808c4b910D972f10f",
  ArbitrumNodeInterface: "0x00000000000000000000000000000000000000C8",
  GelatoRelayAddress: "0xaBcC9b596420A9E9172FD5938620E265a0f9Df92",
  ExternalHandler: '0x82111740dD9a3591e1A212265c94d712bAa76086',//1

  GLP: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  GMX: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  ES_GMX: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  BN_GMX: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  USDG: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  ES_GMX_IOU: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  OpenOceanRouter: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  Vault: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  PositionRouter: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  RewardRouter: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  StakedGmxTracker: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  BonusGmxTracker: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  FeeGmxTracker: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  StakedGlpTracker: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  FeeGlpTracker: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  ExtendedGmxTracker: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  StakedGmxDistributor: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  StakedGlpDistributor: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  GmxVester: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  GlpVester: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  AffiliateVester: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  Router: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  VaultReader: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  Reader: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  GlpManager: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  RewardReader: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  GlpRewardRouter: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
  Timelock: "0x82111740dD9a3591e1A212265c94d712bAa76086",//1
}
};

type ExtractContractNames<T extends object> = {
  [K in keyof T]: keyof T[K];
}[keyof T];

export type ContractName = ExtractContractNames<typeof CONTRACTS>;

export function getContract(chainId: ContractsChainId, name: ContractName): Address {
  if (!CONTRACTS[chainId]) {
    throw new Error(`Unknown chainId ${chainId}`);
  }

  if (!CONTRACTS[chainId][name]) {
    throw new Error(`Unknown contract "${name}" for chainId ${chainId}`);
  }

  return CONTRACTS[chainId][name];
}
