# Json templates for various data types
class GenericFields:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Region:
    def __init__(self, id, region):
        self.id = id
        self.name = region

class Region:
    def __init__(self, id, region, coords, shape, url):
        self.id = id
        self.name = region
        self.coords = coords
        self.shape = shape
        self.url = url


class TonalType:
    def __init__(self, id, tonal_type):
        self.id = id
        self.name = tonal_type


class TonalSource:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class PropulsionType:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class PlatformType:
    def __init__(self, id, name):
        self.id = id
        self.platform_type = name


class PlatformSubType:
    def __init__(self, id, platform_type_id, name):
        self.id = id
        self.platform_sub_type = name
        self.platform_type_id = platform_type_id


class Country:
    def __init__(self, id, regionId, name):
        self.id = id
        self.country = name
        self.region_id = regionId
        self.flag_url = None


class ClassU:
    def __init__(self, id, title, platform_sub_type_id, country_id, remarks, engine, main_propulsion_type_id,
                 backup_propulsion_type_id, propulsion, backup_propulsion, max_speed, tpk, max_rpm, images,
                 ref_id):
        self.id = id
        self.bookmarked = False
        self.title = title
        self.platform_sub_type_id = platform_sub_type_id
        self.country_id = country_id
        self.remarks = remarks
        self.engine = engine
        self.main_propulsion_type_id = main_propulsion_type_id
        self.backup_propulsion_type_id = backup_propulsion_type_id
        self.propulsion = propulsion
        self.backup_propulsion = backup_propulsion
        self.max_speed = max_speed
        self.tpk = tpk
        self.max_rpm = max_rpm
        self.images = images
        self.ref_id = ref_id


class Tonal:
    def __init__(self, id, class_id, tonal_type_id, source, ratio, harmonics, remarks, country_id, platform_type_id,
                 platform_sub_type_id, max_speed, tpk, max_rpm):
        self.id = id
        self.unit_id = class_id
        self.tonal_type_id = tonal_type_id
        self.source = source
        self.ratio = ratio
        self.harmonics = harmonics
        self.remarks = remarks
        self.country_id = country_id
        self.platform_type_id = platform_type_id
        self.platform_sub_type_id = platform_sub_type_id
        self.max_speed = max_speed
        self.tpk = tpk
        self.max_rpm = max_rpm
