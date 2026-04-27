/*
  This files is used to pre-build data during the build process.
  Avoid adding client-side code here, as it can break the build process.
*/
import { CELO, ContractsChainId } from './chains'

export const SWAP_GRAPH_MAX_MARKETS_PER_TOKEN = 5

export type MarketConfig = {
  marketTokenAddress: string
  indexTokenAddress: string
  longTokenAddress: string
  shortTokenAddress: string
}

/*
  ATTENTION
  When adding new markets, please add them also to the end of the list in ./src/configs/static/sortedMarkets.ts
*/
export const MARKETS: Partial<Record<
  ContractsChainId,
  Record<string, MarketConfig>
>> = {
  [CELO]: {
    //new markets
    //wEURm/USD [wEURm-wUSDT]
    '0x38995e0D3c25EE78D45A45A1311A2CA0544b0E6B': {
      marketTokenAddress: '0x38995e0D3c25EE78D45A45A1311A2CA0544b0E6B',
      indexTokenAddress: '0x2350246BAE36EE301B108cA8fE58D795A8DBdb4e',
      longTokenAddress: '0x2350246BAE36EE301B108cA8fE58D795A8DBdb4e',
      shortTokenAddress: '0xd96a1ac57a180a3819633bCE3dC602Bd8972f595',
    },
    //wBTC/USD [wBTC-wUSDT]
    '0xDbBe49A7165F40C79D00bCD3B456AaE887c3d771': {
      marketTokenAddress: '0xDbBe49A7165F40C79D00bCD3B456AaE887c3d771',
      indexTokenAddress: '0x57433eD8eC1FAD60b8E1dcFdD1fBD56aBA19C04C',
      longTokenAddress: '0x57433eD8eC1FAD60b8E1dcFdD1fBD56aBA19C04C',
      shortTokenAddress: '0xd96a1ac57a180a3819633bCE3dC602Bd8972f595',
    },
    //wETH/USD [wETH-wUSDT]
    '0x3d069FFd681B68BF281077516dd9006C2e4c818A': {
      marketTokenAddress: '0x3d069FFd681B68BF281077516dd9006C2e4c818A',
      indexTokenAddress: '0x4C2675e9067Cd7Fc859165AC5F37f1D82d825A1E',
      longTokenAddress: '0x4C2675e9067Cd7Fc859165AC5F37f1D82d825A1E',
      shortTokenAddress: '0xd96a1ac57a180a3819633bCE3dC602Bd8972f595',
    },
    //wCELO/USD [wCELO-wUSDT]
    '0x1f39c2B41af79973b25F65E7a4234bc22aF250D7': {
      marketTokenAddress: '0x1f39c2B41af79973b25F65E7a4234bc22aF250D7',
      indexTokenAddress: '0x5B1B6DCB4E907b9755E27Db88bD62B9750a13C60',
      longTokenAddress: '0x5B1B6DCB4E907b9755E27Db88bD62B9750a13C60',
      shortTokenAddress: '0xd96a1ac57a180a3819633bCE3dC602Bd8972f595',
    },
    //wJPYm/USD [wJPYm-wUSDT]
    '0xaaB05004Ac382adE5E70eEFC3C67035b5F31b990': {
      marketTokenAddress: '0xaaB05004Ac382adE5E70eEFC3C67035b5F31b990',
      indexTokenAddress: '0x29206D4B6183A29Ef5B68494B0850330e98f27F4',
      longTokenAddress: '0x29206D4B6183A29Ef5B68494B0850330e98f27F4',
      shortTokenAddress: '0xd96a1ac57a180a3819633bCE3dC602Bd8972f595',
    },
    //wNGNm/USD [wNGNm-wUSDT]
    '0x1B07C05466D7dC15244969EbCf23520Aba4df9e7': {
      marketTokenAddress: '0x1B07C05466D7dC15244969EbCf23520Aba4df9e7',
      indexTokenAddress: '0xEb8A6C14e625A05F06eA914Db627dd65175b4505',
      longTokenAddress: '0xEb8A6C14e625A05F06eA914Db627dd65175b4505',
      shortTokenAddress: '0xd96a1ac57a180a3819633bCE3dC602Bd8972f595',
    },
    //wAUDm/USD [wAUDm-wUSDT]
    '0x22476a639D1bBDDE1919A226347360b32A2385Fe': {
      marketTokenAddress: '0x22476a639D1bBDDE1919A226347360b32A2385Fe',
      indexTokenAddress: '0x91CA0318Fc30D728640f0E6329205eE1F538F17B',
      longTokenAddress: '0x91CA0318Fc30D728640f0E6329205eE1F538F17B',
      shortTokenAddress: '0xd96a1ac57a180a3819633bCE3dC602Bd8972f595',
    },
    //wGBPm/USD [wGBPm-wUSDT]
    '0xc439330b3D59Be316936Ff62d1d22b377656Fc20': {
      marketTokenAddress: '0xc439330b3D59Be316936Ff62d1d22b377656Fc20',
      indexTokenAddress: '0x7Ef503a2722cdfa7E99f2A59771f7E2390c2DF76',
      longTokenAddress: '0x7Ef503a2722cdfa7E99f2A59771f7E2390c2DF76',
      shortTokenAddress: '0xd96a1ac57a180a3819633bCE3dC602Bd8972f595',
    },
    //wXAUT/USD [wXAUT-wUSDT]
    '0x0645a00C8b93c62c86297C7D0BfC805178c738e0': {
      marketTokenAddress: '0x0645a00C8b93c62c86297C7D0BfC805178c738e0',
      indexTokenAddress: '0xdffa5c533eb195625D15C34A82f5822C35f4EC2B',
      longTokenAddress: '0xdffa5c533eb195625D15C34A82f5822C35f4EC2B',
      shortTokenAddress: '0xd96a1ac57a180a3819633bCE3dC602Bd8972f595',
    },
  },
}
