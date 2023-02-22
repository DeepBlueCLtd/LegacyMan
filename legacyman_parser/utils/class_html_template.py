
class ClassU:
    def __init__(self,
                 id,
                 class_u,
                 sub_category,
                 country,
                 designator,
                 power,
                 shaft_blade,
                 bhp,
                 av_temp,
                 reduction_ratio,
                 has_tonal,
                 tonal_href):
        self.id = id
        self.class_u = class_u
        self.sub_category = sub_category
        self.country = country
        self.designator = designator
        self.power = power
        self.shaft_blade = shaft_blade
        self.bhp = bhp
        self.av_temp = av_temp
        self.reduction_ratio = reduction_ratio
        self.has_tonal = has_tonal
        self.tonal_href = tonal_href

    def __str__(self):
        return "{} [{}] of {} is powered by {} " \
               "and has {}, {}, {}, {}, and {}{}".format(self.class_u,
                                                         self.sub_category,
                                                         self.country,
                                                         self.power,
                                                         self.designator,
                                                         self.shaft_blade,
                                                         self.bhp,
                                                         self.av_temp,
                                                         self.reduction_ratio,
                                                         (". Tonal ==> " + self.tonal_href) if
                                                         self.has_tonal else "")
