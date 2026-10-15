"""Civilisation rule modules (r4_design §2): each a Civ subclass with its growth params, its facade grammar and its
marks.  The engine (grow.py, pick.py) is generic; everything that makes a city read as its civilisation is here --
the two milestone civs by hand, the rest as FamilyCiv SPECs (civ/family.py)."""
from civ.andean_neo import AndeanNeo
from civ.chongqing_cliff import ChongqingCliff
from civ.hakka_tulou import HakkaTulou
from civ.manila_estero import ManilaEstero
from civ.siam_khlong import SiamKhlong
from civ.straits_shophouse import StraitsShophouse
from civ.tibetan_lhasa import TibetanLhasa
from civ.viet_tube import VietTube
from civ.caucasian_balcony import CaucasianBalcony
from civ.jiangnan_water import JiangnanWater
from civ.korean_hillside import KoreanHillside
from civ.kulla_stone import KullaStone
from civ.ottoman_timber import OttomanTimber
from civ.scots_lands import ScotsLands
from civ.cycladic import Cycladic
from civ.knights_harbour import KnightsHarbour
from civ.lusitanian_hill import LusitanianHill
from civ.mardin_terraces import MardinTerraces
from civ.rupestrian_terraces import RupestrianTerraces
from civ.tyrrhenian_canyon import TyrrhenianCanyon
from civ.ganga_ghat import GangaGhat
from civ.karachi import Karachi
from civ.mughal_walled import MughalWalled
from civ.newar import Newar
from civ.rajput_sandstone import RajputSandstone
from civ.silk_road import SilkRoad
from civ.cairene_mamluk import CaireneMamluk
from civ.hejazi_roshan import HejaziRoshan
from civ.levantine_courtyard import LevantineCourtyard
from civ.omani_oasis import OmaniOasis
from civ.persian_desert import PersianDesert
from civ.saharan_kasbah import SaharanKasbah
from civ.creole_colonial import CreoleColonial
from civ.hanseatic_gable import HanseaticGable
from civ.hk_neon_canyon import HkNeonCanyon
from civ.iberian_white import IberianWhite
from civ.japan_yokocho import JapanYokocho
from civ.kowloon_walled import KowloonWalled
from civ.latin_hillside import LatinHillside
from civ.maghrebi_medina import MaghrebiMedina
from civ.mzab_ghadames import MzabGhadames
from civ.nouvelle_france import NouvelleFrance
from civ.taipei_tiepi import TaipeiTiepi
from civ.yemeni_tower import YemeniTower

CIVS = {c.id: c for c in (MaghrebiMedina, KowloonWalled, YemeniTower, MzabGhadames, HanseaticGable, JapanYokocho,
                          LatinHillside, CreoleColonial, HkNeonCanyon, TaipeiTiepi, NouvelleFrance, AndeanNeo,
                          IberianWhite, ChongqingCliff, HejaziRoshan, CaireneMamluk, LevantineCourtyard,
                          SaharanKasbah, OmaniOasis, PersianDesert, SilkRoad, Karachi, MughalWalled, RajputSandstone,
                          GangaGhat, Newar, TyrrhenianCanyon, RupestrianTerraces, Cycladic, KnightsHarbour,
                          LusitanianHill, MardinTerraces, OttomanTimber, KullaStone, CaucasianBalcony, ScotsLands,
                          JiangnanWater, KoreanHillside, HakkaTulou, TibetanLhasa, VietTube, StraitsShophouse,
                          SiamKhlong, ManilaEstero)}


def civ_for(cid, isl, rng):
    return CIVS[cid](isl, rng)
