"""
Thermal camera
================================================================================

COLORS:
    List of 972 constants (2 btes) representing RGB565 (Big Endien) colors


* Author(s): Paulo Teixeira, inspired in some list I lost the link...


Implementation Notes
--------------------

Uncomment any color to be used in GUI

"""

class Color:  # pylint: disable=too-few-public-methods
    """Enum-like class of usable colors"""
    
#     ABSOLUTE_ZERO = 0x5702
#     ACID_GREEN = 0xe3b5
#     AERO = 0xdd7d
#     AERO_BLUE = 0x5ac7
#     AFRICAN_VIOLET = 0x37b4
#     AIR_SUPERIORITY_BLUE = 0x1875
#     ALABASTER = 0x5cef
#     ALICE_BLUE = 0xdff7
#     ALLOY_ORANGE = 0x02c3
#     ALMOND = 0xf9ee
#     AMARANTH = 0x4ae1
#     AMARANTH_M_AND_P = 0x4d99
#     AMARANTH_PINK = 0xf7f4
#     AMARANTH_PURPLE = 0x29a9
#     AMARANTH_RED = 0x05d1
#     AMAZON = 0xca3b
#     AMBER = 0xe0fd
#     AMBER_SAE_ECE = 0xe0fb
#     AMETHYST = 0x399b
#     ANDROID_GREEN = 0x27a6
#     ANTIQUE_BRASS = 0xaecc
#     ANTIQUE_BRONZE = 0xe362
#     ANTIQUE_FUCHSIA = 0xf092
#     ANTIQUE_RUBY = 0xc580
#     ANTIQUE_WHITE = 0x5aff
#     AO_ENGLISH = 0x0004
#     APPLE_GREEN = 0xa08d
#     APRICOT = 0x76fe
#     AQUA = 0xff07
#     AQUAMARINE = 0xfa7f
#     ARCTIC_LIME = 0xe2d7
#     ARMY_GREEN = 0x844a
#     ARTICHOKE = 0xaf8c
#     ARYLIDE_YELLOW = 0xadee
#     ASH_GRAY = 0xf6b5
#     ASPARAGUS = 0x4d85
#     ATOMIC_TANGERINE = 0xccfc
#     AUBURN = 0x45a1
#     AUREOLIN = 0x60ff
#     AVOCADO = 0x0054
#     AZURE = 0xff03
#     AZURE_X11_WEB_COLOR = 0xfff7
#     BABY_BLUE = 0x7e8e
#     BABY_BLUE_EYES = 0x5ea6
#     BABY_PINK = 0x18f6
#     BABY_POWDER = 0xffff
#     BAKER_MILLER_PINK = 0x95fc
#     BANANA_MANIA = 0x36ff
#     BARBIE_PINK = 0xd0d8
#     BARN_RED = 0x4078
#     BATTLESHIP_GREY = 0x3084
#     BEAU_BLUE = 0xbcbe
#     BEAVER = 0x0e9c
#     BEIGE = 0xbbf7
#     B_DAZZLED_BLUE = 0xd22a
#     BIG_DIP_O_RUBY = 0x2899
#     BISQUE = 0x38ff
#     BISTRE = 0x4339
#     BISTRE_BROWN = 0x8293
#     BITTER_LEMON = 0x01cf
#     BITTER_LIME = 0xe0bf
#     BITTERSWEET = 0x6bfb
#     BITTERSWEET_SHIMMER = 0x6aba
    BLACK = 0x0000
#     BLACK_BEAN = 0x6038
#     BLACK_CHOCOLATE = 0xc218
#     BLACK_COFFEE = 0x6539
#     BLACK_CORAL = 0x0d53
#     BLACK_OLIVE = 0xe639
#     BLACK_SHADOWS = 0x76bd
#     BLANCHED_ALMOND = 0x59ff
#     BLAST_OFF_BRONZE = 0x8ca3
#     BLEU_DE_FRANCE = 0x7c34
#     BLIZZARD_BLUE = 0x3daf
#     BLOND = 0x97ff
#     BLOOD_RED = 0x0060
    BLUE = 0x1f00
#     BLUE_CRAYOLA = 0xbf1b
#     BLUE_MUNSELL = 0x9504
#     BLUE_NCS = 0x3704
#     BLUE_PANTONE = 0xd500
#     BLUE_PIGMENT = 0x9331
#     BLUE_RYB = 0x3f02
#     BLUE_BELL = 0x1aa5
#     BLUE_GRAY = 0xd964
#     BLUE_GREEN = 0xd70c
#     BLUE_GREEN_COLOR_WHEEL = 0x6802
#     BLUE_JEANS = 0x7d5d
#     BLUE_SAPPHIRE = 0x1013
#     BLUE_VIOLET = 0x5c89
#     BLUE_VIOLET_CRAYOLA = 0x3773
#     BLUE_VIOLET_COLOR_WHEEL = 0xcf48
#     BLUE_YONDER = 0x9453
#     BLUETIFUL = 0x5c3b
#     BLUSH = 0xf0da
#     BOLE = 0x277a
#     BONE = 0xd9e6
#     BOTTLE_GREEN = 0x4903
#     BRANDY = 0x0782
#     BRICK_RED = 0x0aca
#     BRIGHT_GREEN = 0xe067
#     BRIGHT_LILAC = 0x9ddc
#     BRIGHT_MAROON = 0x09c1
#     BRIGHT_NAVY_BLUE = 0xba1b
#     BRIGHT_YELLOW_CRAYOLA = 0x43fd
#     BRILLIANT_ROSE = 0xb4fa
#     BRINK_PINK = 0x0ffb
#     BRITISH_RACING_GREEN = 0x0402
#     BRONZE = 0xe6cb
#     BROWN = 0xa18a
#     BROWN_SUGAR = 0x69ab
#     BRUNSWICK_GREEN = 0x671a
#     BUD_GREEN = 0xac7d
#     BUFF = 0x30fe
#     BURGUNDY = 0x0480
#     BURLYWOOD = 0xd0dd
#     BURNISHED_BROWN = 0xcea3
#     BURNT_ORANGE = 0xa0ca
#     BURNT_SIENNA = 0xaaeb
#     BURNT_UMBER = 0x8489
#     BYZANTINE = 0x94b9
#     BYZANTIUM = 0x4c71
#     CADET = 0x4e53
#     CADET_BLUE = 0xf45c
#     CADET_BLUE_CRAYOLA = 0x98ad
#     CADET_GREY = 0x1695
#     CADMIUM_GREEN = 0x4703
#     CADMIUM_ORANGE = 0x25ec
#     CADMIUM_RED = 0x04e0
#     CADMIUM_YELLOW = 0xa0ff
#     CAFE_AU_LAIT = 0xcba3
#     CAFE_NOIR = 0xa449
#     CAMBRIDGE_BLUE = 0x15a6
#     CAMEL = 0xcdc4
#     CAMEO_PINK = 0xd9ed
#     CANARY = 0xf3ff
#     CANARY_YELLOW = 0x60ff
#     CANDY_APPLE_RED = 0x40f8
#     CANDY_PINK = 0x8fe3
#     CAPRI = 0xff05
#     CAPUT_MORTUUM = 0x2459
#     CARDINAL = 0xe7c0
#     CARIBBEAN_GREEN = 0x7306
#     CARMINE = 0x0390
#     CARMINE_M_AND_P = 0x08d0
#     CARNATION_PINK = 0x39fd
#     CARNELIAN = 0xc3b0
#     CAROLINA_BLUE = 0x1a55
#     CARROT_ORANGE = 0x84ec
#     CASTLETON_GREEN = 0xa702
#     CATAWBA = 0xa871
#     CEDAR_CHEST = 0xc9ca
#     CELADON = 0x15af
#     CELADON_BLUE = 0xd403
#     CELADON_GREEN = 0x2f2c
#     CELESTE = 0xffb7
#     CELTIC_BLUE = 0x5923
#     CERISE = 0x8cd9
#     CERULEAN = 0xd403
#     CERULEAN_BLUE = 0x972a
#     CERULEAN_FROST = 0xd86c
#     CERULEAN_CRAYOLA = 0x7a1d
#     CG_BLUE = 0xd403
#     CG_RED = 0xe6e1
#     CHAMPAGNE = 0x39f7
#     CHAMPAGNE_PINK = 0xf9f6
#     CHARCOAL = 0x2932
#     CHARLESTON_GREEN = 0x4521
#     CHARM_PINK = 0x75e4
#     CHARTREUSE_TRADITIONAL = 0xe0df
#     CHARTREUSE_WEB = 0xe07f
#     CHERRY_BLOSSOM_PINK = 0xb8fd
#     CHESTNUT = 0x2692
#     CHILI_RED = 0xe5e1
#     CHINA_PINK = 0x74db
#     CHINA_ROSE = 0x8daa
#     CHINESE_RED = 0xc3a9
#     CHINESE_VIOLET = 0x1183
#     CHINESE_YELLOW = 0x80fd
#     CHOCOLATE_TRADITIONAL = 0xe079
#     CHOCOLATE_WEB = 0x43d3
#     CHOCOLATE_COSMOS = 0x8358
#     CHROME_YELLOW = 0x20fd
#     CINEREOUS = 0x0f9c
#     CINNABAR = 0x06e2
#     CINNAMON_SATIN = 0x0fcb
#     CITRINE = 0x81e6
#     CITRON = 0x439d
#     CLARET = 0xa678
#     COBALT_BLUE = 0x3502
#     COCOA_BROWN = 0x43d3
#     COFFEE = 0x666a
#     COLUMBIA_BLUE = 0xddbe
#     CONGO_PINK = 0x0ffc
#     COOL_GREY = 0x958c
#     COPPER = 0x86bb
#     COPPER_CRAYOLA = 0x4cdc
#     COPPER_PENNY = 0x6dab
#     COPPER_RED = 0x6acb
#     COPPER_ROSE = 0x2c9b
#     COQUELICOT = 0xc0f9
#     CORAL = 0xeafb
#     CORAL_PINK = 0x0ffc
#     CORDOVAN = 0xe889
#     CORN = 0x6bff
#     CORNELL_RED = 0xc3b0
#     CORNFLOWER_BLUE = 0xbd64
#     CORNSILK = 0xdbff
#     COSMIC_COBALT = 0x7129
#     COSMIC_LATTE = 0xdcff
#     COYOTE_BROWN = 0x0783
#     COTTON_CANDY = 0xfbfd
#     CREAM = 0xfaff
#     CRIMSON = 0xa7d8
#     CRIMSON_UA = 0xc698
#     CRYSTAL = 0xdba6
#     CULTURED = 0xbef7
#     CYAN = 0xff07
#     CYAN_PROCESS = 0xbd05
#     CYBER_GRAPE = 0x0f5a
#     CYBER_YELLOW = 0x80fe
#     CYCLAMEN = 0x74f3
#     DARK_BLUE_GRAY = 0x3363
#     DARK_BROWN = 0x0462
#     DARK_BYZANTIUM = 0xca59
#     DARK_CORNFLOWER_BLUE = 0x1122
#     DARK_CYAN = 0x5104
#     DARK_ELECTRIC_BLUE = 0x4f53
#     DARK_GOLDENROD = 0x21bc
#     DARK_GREEN = 0x8401
#     DARK_GREEN_X11 = 0x2003
#     DARK_JUNGLE_GREEN = 0x2419
#     DARK_KHAKI = 0xadbd
#     DARK_LAVA = 0xe649
#     DARK_LIVER = 0x4952
#     DARK_LIVER_HORSES = 0xe651
#     DARK_MAGENTA = 0x1188
#     DARK_MOSS_GREEN = 0xe44a
#     DARK_OLIVE_GREEN = 0x4553
#     DARK_ORANGE = 0x60fc
#     DARK_ORCHID = 0x9999
#     DARK_PASTEL_GREEN = 0x0706
#     DARK_PURPLE = 0xc630
#     DARK_RED = 0x0088
#     DARK_SALMON = 0xafec
#     DARK_SEA_GREEN = 0xf18d
#     DARK_SIENNA = 0xa238
#     DARK_SKY_BLUE = 0xfa8d
#     DARK_SLATE_BLUE = 0xf149
#     DARK_SLATE_GRAY = 0x692a
#     DARK_SPRING_GREEN = 0x8813
#     DARK_TURQUOISE = 0x7a06
#     DARK_VIOLET = 0x1a90
#     DARTMOUTH_GREEN = 0x8703
#     DAVY_S_GREY = 0xaa52
#     DEEP_CERISE = 0x90d9
#     DEEP_CHAMPAGNE = 0xb4fe
#     DEEP_CHESTNUT = 0x69ba
#     DEEP_JUNGLE_GREEN = 0x4902
#     DEEP_PINK = 0xb2f8
#     DEEP_SAFFRON = 0xc6fc
#     DEEP_SKY_BLUE = 0xff05
#     DEEP_SPACE_SPARKLE = 0x2d4b
#     DEEP_TAUPE = 0xec7a
#     DENIM = 0x1713
#     DENIM_BLUE = 0x1622
#     DESERT = 0xcdc4
#     DESERT_SAND = 0x55ee
#     DIM_GRAY = 0x4d6b
#     DODGER_BLUE = 0x9f1c
#     DOGWOOD_ROSE = 0xcdd0
#     DRAB = 0x8293
#     DUKE_BLUE = 0x1300
#     DUTCH_WHITE = 0xf7ee
#     EARTH_YELLOW = 0x4be5
#     EBONY = 0xea52
#     ECRU = 0x90c5
#     EERIE_BLACK = 0xc318
#     EGGPLANT = 0x0a62
#     EGGSHELL = 0x5af7
#     EGYPTIAN_BLUE = 0xb411
#     EIGENGRAU = 0xa310
#     ELECTRIC_BLUE = 0xdf7f
#     ELECTRIC_GREEN = 0xe007
#     ELECTRIC_INDIGO = 0x1f68
#     ELECTRIC_LIME = 0xe0cf
#     ELECTRIC_PURPLE = 0x1fb8
#     ELECTRIC_VIOLET = 0x1f88
#     EMERALD = 0x4f56
#     EMINENCE = 0x9069
#     ENGLISH_GREEN = 0x671a
#     ENGLISH_LAVENDER = 0x12b4
#     ENGLISH_RED = 0x4aaa
#     ENGLISH_VERMILLION = 0x29ca
#     ENGLISH_VIOLET = 0xeb51
#     ERIN = 0xe807
#     ETON_BLUE = 0x5496
#     FALLOW = 0xcdc4
#     FALU_RED = 0xc380
#     FANDANGO = 0x91b1
#     FANDANGO_PINK = 0x90da
#     FASHION_FUCHSIA = 0x14f0
#     FAWN = 0x4ee5
#     FELDGRAU = 0xea4a
#     FERN_GREEN = 0xc84b
#     FIELD_DRAB = 0xa36a
#     FIERY_ROSE = 0xaefa
#     FIREBRICK = 0x04b1
#     FIRE_ENGINE_RED = 0x05c9
#     FIRE_OPAL = 0xe9ea
#     FLAME = 0xc4e2
#     FLAX = 0xf0ee
#     FLIRT = 0x0da0
#     FLORAL_WHITE = 0xdeff
#     FLUORESCENT_BLUE = 0xbd17
#     FOREST_GREEN_CRAYOLA = 0x2e5d
#     FOREST_GREEN_TRADITIONAL = 0x2402
#     FOREST_GREEN_WEB = 0x4424
#     FRENCH_BEIGE = 0xcba3
#     FRENCH_BISTRE = 0x6983
#     FRENCH_BLUE = 0x9703
#     FRENCH_FUCHSIA = 0xf2f9
#     FRENCH_LILAC = 0x1183
#     FRENCH_LIME = 0xe79f
#     FRENCH_MAUVE = 0x9ad3
#     FRENCH_PINK = 0x73fb
#     FRENCH_RASPBERRY = 0x69c1
#     FRENCH_ROSE = 0x51f2
#     FRENCH_SKY_BLUE = 0xbf75
#     FRENCH_VIOLET = 0x3988
#     FROSTBITE = 0xb4e9
#     FUCHSIA = 0x1ff8
#     FUCHSIA_CRAYOLA = 0xb8c2
#     FUCHSIA_PURPLE = 0xcfc9
#     FUCHSIA_ROSE = 0x0ec2
#     FULVOUS = 0x20e4
#     FUZZY_WUZZY = 0x0382
#     GAINSBORO = 0xfbde
#     GAMBOGE = 0xc1e4
#     GENERIC_VIRIDIAN = 0xec03
#     GHOST_WHITE = 0xdfff
#     GLAUCOUS = 0x1664
#     GLOSSY_GRAPE = 0x96ac
#     GO_GREEN = 0x4c05
#     GOLD = 0xe0a3
#     GOLD_METALLIC = 0x66d5
#     GOLD_WEB_GOLDEN = 0xa0fe
#     GOLD_CRAYOLA = 0xf1e5
#     GOLD_FUSION = 0xa983
#     GOLDEN_BROWN = 0x229b
#     GOLDEN_POPPY = 0x00fe
#     GOLDEN_YELLOW = 0xe0fe
#     GOLDENROD = 0x24dd
#     GRANITE_GRAY = 0x2c63
#     GRANNY_SMITH_APPLE = 0x34af
    GRAY = 0x1084
#     GRAY_2 = 0xf7bd
    GREEN = 0xe007
#     GREEN_CRAYOLA = 0x6f1d
#     GREEN_WEB = 0x0004
#     GREEN_MUNSELL = 0x4e05
#     GREEN_NCS = 0xed04
#     GREEN_PANTONE = 0x6805
#     GREEN_PIGMENT = 0x2a05
#     GREEN_RYB = 0x8665
#     GREEN_BLUE = 0x3613
#     GREEN_BLUE_CRAYOLA = 0x392c
#     GREEN_CYAN = 0xcc04
#     GREEN_LIZARD = 0xa6a7
#     GREEN_SHEEN = 0x746d
#     GREEN_YELLOW = 0xe5af
#     GREEN_YELLOW_CRAYOLA = 0x52f7
#     GRULLO = 0xd0ac
#     GUNMETAL = 0xa729
#     HAN_BLUE = 0x7943
#     HAN_PURPLE = 0xdf50
#     HANSA_YELLOW = 0xadee
#     HARLEQUIN = 0xe03f
#     HARVEST_GOLD = 0x80dc
#     HEAT_WAVE = 0xc0fb
#     HELIOTROPE = 0x9fdb
#     HELIOTROPE_GRAY = 0xd5ac
#     HOLLYWOOD_CERISE = 0x14f0
#     HONEYDEW = 0xfef7
#     HONOLULU_BLUE = 0x7603
#     HOOKER_S_GREEN = 0xcd4b
#     HOT_MAGENTA = 0xf9f8
#     HOT_PINK = 0x56fb
#     HUNTER_GREEN = 0xe732
#     ICEBERG = 0x3a75
#     ICTERINE = 0xabff
#     ILLUMINATING_EMERALD = 0x8e34
#     IMPERIAL_RED = 0x47e9
#     INCHWORM = 0x6bb7
#     INDEPENDENCE = 0x8d4a
#     INDIA_GREEN = 0x4114
#     INDIAN_RED = 0xebca
#     INDIAN_YELLOW = 0x4ae5
#     INDIGO = 0x1048
#     INDIGO_DYE = 0x0d02
#     INTERNATIONAL_ORANGE_1 = 0x60fa
#     INTERNATIONAL_ORANGE_2 = 0xa1b8
#     INTERNATIONAL_ORANGE_3 = 0xa5c1
#     IRIS = 0x795a
#     IRRESISTIBLE = 0x2db2
#     ISABELLINE = 0x9df7
#     ITALIAN_SKY_BLUE = 0xffb7
#     IVORY = 0xfeff
#     JADE = 0x4d05
#     JAPANESE_CARMINE = 0x4699
#     JAPANESE_VIOLET = 0x8a59
#     JASMINE = 0xeffe
#     JAZZBERRY_JAM = 0x4ba0
#     JET = 0xa631
#     JONQUIL = 0x42f6
#     JUNE_BUD = 0xcabe
#     JUNGLE_GREEN = 0x502d
#     KELLY_GREEN = 0xc24d
#     KEPPEL = 0x933d
#     KEY_LIME = 0xb1ef
#     KHAKI_WEB = 0x92c5
#     KHAKI_X11_LIGHT_KHAKI = 0x31f7
#     KOBE = 0x6289
#     KOBI = 0xf8e4
#     KOBICHA = 0x246a
#     KOMBU_GREEN = 0x0632
#     KSU_PURPLE = 0x5151
#     LANGUID_LAVENDER = 0x5bd6
#     LAPIS_LAZULI = 0x1323
#     LASER_LEMON = 0xecff
#     LAUREL_GREEN = 0xd3ad
#     LAVA = 0x84c8
#     LAVENDER_FLORAL = 0xfbb3
#     LAVENDER_WEB = 0x3fe7
#     LAVENDER_BLUE = 0x7fce
#     LAVENDER_BLUSH = 0x9eff
#     LAVENDER_GRAY = 0x1ac6
#     LAWN_GREEN = 0xe07f
#     LEMON = 0xa0ff
#     LEMON_CHIFFON = 0xd9ff
#     LEMON_CURRY = 0x03cd
#     LEMON_GLACIER = 0xe0ff
#     LEMON_MERINGUE = 0x57f7
#     LEMON_YELLOW = 0xa9ff
#     LEMON_YELLOW_CRAYOLA = 0xf3ff
#     LIBERTY = 0xd452
#     LIGHT_BLUE = 0xdcae
#     LIGHT_CORAL = 0x10f4
#     LIGHT_CORNFLOWER_BLUE = 0x7d96
#     LIGHT_CYAN = 0xffe7
#     LIGHT_FRENCH_BEIGE = 0x6fcd
#     LIGHT_GOLDENROD = 0xdaff
#     LIGHT_GRAY = 0x9ad6
#     LIGHT_GREEN = 0x7297
#     LIGHT_ORANGE = 0xd6fe
#     LIGHT_PERIWINKLE = 0x5cc6
#     LIGHT_PINK = 0xb8fd
#     LIGHT_SALMON = 0x0ffd
#     LIGHT_SEA_GREEN = 0x9525
#     LIGHT_SKY_BLUE = 0x7f86
#     LIGHT_SLATE_GRAY = 0x5374
#     LIGHT_STEEL_BLUE = 0x3bb6
#     LIGHT_YELLOW = 0xfcff
#     LILAC = 0x19cd
#     LILAC_LUSTER = 0xd5ac
#     LIME_COLOR_WHEEL = 0xe0bf
#     LIME_WEB_X11_GREEN = 0xe007
#     LIME_GREEN = 0x6636
#     LINCOLN_GREEN = 0xc01a
#     LINEN = 0x9cff
#     LION = 0xcdc4
#     LISERAN_PURPLE = 0x74db
#     LITTLE_BOY_BLUE = 0x1b6d
#     LIVER = 0x6862
#     LIVER_DOGS = 0x65bb
#     LIVER_ORGAN = 0x6369
#     LIVER_CHESTNUT = 0xaa9b
#     LIVID = 0xd964
#     MACARONI_AND_CHEESE = 0xf1fd
#     MADDER_LAKE = 0x86c9
#     MAGENTA = 0x1ff8
#     MAGENTA_CRAYOLA = 0x94f2
#     MAGENTA_DYE = 0xefc8
#     MAGENTA_PANTONE = 0x0fd2
#     MAGENTA_PROCESS = 0x12f8
#     MAGENTA_HAZE = 0x2e9a
#     MAGIC_MINT = 0x9aaf
#     MAGNOLIA = 0x5af7
#     MAHOGANY = 0x00c2
#     MAIZE = 0x6bff
#     MAIZE_CRAYOLA = 0x29f6
#     MAJORELLE_BLUE = 0x9b62
#     MALACHITE = 0xca0e
#     MANATEE = 0xd594
#     MANDARIN = 0xc9f3
#     MANGO = 0xe0fd
#     MANGO_TANGO = 0x08fc
#     MANTIS = 0x0c76
#     MARDI_GRAS = 0x1088
#     MARIGOLD = 0x04ed
#     MAROON_CRAYOLA = 0x09c1
#     MAROON_WEB = 0x0080
#     MAROON_X11 = 0x8cb1
#     MAUVE = 0x9fe5
#     MAUVE_TAUPE = 0xed92
#     MAUVELOUS = 0xd5ec
#     MAXIMUM_BLUE = 0x5945
#     MAXIMUM_BLUE_GREEN = 0xf735
#     MAXIMUM_BLUE_PURPLE = 0x7cad
#     MAXIMUM_GREEN = 0x665c
#     MAXIMUM_GREEN_YELLOW = 0x2adf
#     MAXIMUM_PURPLE = 0x9071
#     MAXIMUM_RED = 0x04d9
#     MAXIMUM_RED_PURPLE = 0xcfa1
#     MAXIMUM_YELLOW = 0xc6ff
#     MAXIMUM_YELLOW_RED = 0xc9f5
#     MAY_GREEN = 0x884c
#     MAYA_BLUE = 0x1f76
#     MEDIUM_AQUAMARINE = 0xf566
#     MEDIUM_BLUE = 0x1900
#     MEDIUM_CANDY_APPLE_RED = 0x25e0
#     MEDIUM_CARMINE = 0x06aa
#     MEDIUM_CHAMPAGNE = 0x35f7
#     MEDIUM_ORCHID = 0xbaba
#     MEDIUM_PURPLE = 0x9b93
#     MEDIUM_SEA_GREEN = 0x8e3d
#     MEDIUM_SLATE_BLUE = 0x5d7b
#     MEDIUM_SPRING_GREEN = 0xd307
#     MEDIUM_TURQUOISE = 0x994e
#     MEDIUM_VIOLET_RED = 0xb0c0
#     MELLOW_APRICOT = 0xcffd
#     MELLOW_YELLOW = 0xeffe
#     MELON = 0xd5fd
#     METALLIC_GOLD = 0x66d5
#     METALLIC_SEAWEED = 0xf10b
#     METALLIC_SUNBURST = 0xe79b
#     MEXICAN_PINK = 0x0fe0
#     MIDDLE_BLUE = 0xbc7e
#     MIDDLE_BLUE_GREEN = 0xd98e
#     MIDDLE_BLUE_PURPLE = 0x978b
#     MIDDLE_GREY = 0x308c
#     MIDDLE_GREEN = 0x6a4c
#     MIDDLE_GREEN_YELLOW = 0xecad
#     MIDDLE_PURPLE = 0x16dc
#     MIDDLE_RED = 0x6ee4
#     MIDDLE_RED_PURPLE = 0x8aa2
#     MIDDLE_YELLOW = 0x40ff
#     MIDDLE_YELLOW_RED = 0x8eed
#     MIDNIGHT = 0x2e71
#     MIDNIGHT_BLUE = 0xce18
#     MIDNIGHT_GREEN_EAGLE_GREEN = 0x4a02
#     MIKADO_YELLOW = 0x21fe
#     MIMI_PINK = 0xddfe
#     MINDARO = 0xd1e7
#     MING = 0xaf33
#     MINION_YELLOW = 0x0af7
#     MINT = 0xb13d
#     MINT_CREAM = 0xfff7
#     MINT_GREEN = 0xf39f
#     MISTY_MOSS = 0xaebd
#     MISTY_ROSE = 0x3cff
#     MODE_BEIGE = 0x8293
#     MORNING_BLUE = 0x138d
#     MOSS_GREEN = 0xcb8c
#     MOUNTAIN_MEADOW = 0xd135
#     MOUNTBATTEN_PINK = 0xd19b
#     MSU_GREEN = 0x271a
#     MULBERRY = 0x51c2
#     MULBERRY_CRAYOLA = 0x93ca
#     MUSTARD = 0xcbfe
#     MYRTLE_GREEN = 0xce33
#     MYSTIC = 0x90d2
#     MYSTIC_MAROON = 0x0faa
#     NADESHIKO_PINK = 0x78f5
#     NAPLES_YELLOW = 0xcbfe
#     NAVAJO_WHITE = 0xf5fe
#     NAVY_BLUE = 0x1000
#     NAVY_BLUE_CRAYOLA = 0xba1b
#     NEON_BLUE = 0x3f43
#     NEON_CARROT = 0x08fd
#     NEON_GREEN = 0xe23f
#     NEON_FUCHSIA = 0x0cfa
#     NEW_YORK_PINK = 0x0fd4
#     NICKEL = 0xae73
#     NON_PHOTO_BLUE = 0xfda6
#     NYANZA = 0xfbef
#     OCEAN_BLUE = 0x164a
#     OCEAN_GREEN = 0xf24d
#     OCHRE = 0xa4cb
#     OLD_BURGUNDY = 0x8541
#     OLD_GOLD = 0xa7cd
#     OLD_LACE = 0xbcff
#     OLD_LAVENDER = 0x4f7b
#     OLD_MAUVE = 0x8861
#     OLD_ROSE = 0x10c4
#     OLD_SILVER = 0x3084
#     OLIVE = 0x0084
#     OLIVE_DRAB_1 = 0x1784
#     OLIVE_DRAB_2 = 0xe601
#     OLIVE_GREEN = 0x8bb5
#     OLIVINE = 0xce9d
#     ONYX = 0xc731
#     OPAL = 0x17ae
#     OPERA_MAUVE = 0x34b4
#     ORANGE = 0xe0fb
#     ORANGE_CRAYOLA = 0xa7fb
#     ORANGE_PANTONE = 0xc0fa
#     ORANGE_WEB = 0x20fd
#     ORANGE_PEEL = 0xe0fc
#     ORANGE_RED = 0x43fb
#     ORANGE_RED_CRAYOLA = 0x89fa
#     ORANGE_SODA = 0xc7fa
#     ORANGE_YELLOW = 0xe3f5
#     ORANGE_YELLOW_CRAYOLA = 0xadfe
#     ORCHID = 0x9adb
#     ORCHID_PINK = 0xf9f5
#     ORCHID_CRAYOLA = 0xfae4
#     OUTER_SPACE_CRAYOLA = 0xc729
#     OUTRAGEOUS_ORANGE = 0x69fb
#     OXBLOOD = 0x0480
#     OXFORD_BLUE = 0x0801
#     OU_CRIMSON_RED = 0xa280
#     PACIFIC_BLUE = 0x591d
#     PAKISTAN_GREEN = 0x2003
#     PALATINATE_PURPLE = 0x4c69
#     PALE_AQUA = 0xbcbe
#     PALE_CERULEAN = 0x3c9e
#     PALE_DOGWOOD = 0xd3eb
#     PALE_PINK = 0xdbfe
#     PALE_PURPLE_PANTONE = 0x3fff
#     PALE_SILVER = 0x17ce
#     PALE_SPRING_BUD = 0x57ef
#     PALE_VIOLET_RED = 0x92db
#     PANSY_PURPLE = 0xc978
#     PAOLO_VERONESE_GREEN = 0xcf04
#     PAPAYA_WHIP = 0x7aff
#     PARADISE_PINK = 0xece1
#     PARCHMENT = 0x5af7
#     PARIS_GREEN = 0x4f56
#     PASTEL_PINK = 0x34dd
#     PATRIARCH = 0x1080
#     PAYNE_S_GREY = 0x4f53
#     PEACH = 0x36ff
#     PEACH_CRAYOLA = 0x54fe
#     PEACH_PUFF = 0xd7fe
#     PEAR = 0x06d7
#     PEARLY_PURPLE = 0x54b3
#     PERIWINKLE = 0x7fce
#     PERIWINKLE_CRAYOLA = 0x7cc6
#     PERMANENT_GERANIUM_LAKE = 0x65e1
#     PERSIAN_BLUE = 0xd719
#     PERSIAN_GREEN = 0x3205
#     PERSIAN_INDIGO = 0x8f30
#     PERSIAN_ORANGE = 0x8bdc
#     PERSIAN_PINK = 0xf7f3
#     PERSIAN_PLUM = 0xe370
#     PERSIAN_RED = 0x86c9
#     PERSIAN_ROSE = 0x54f9
#     PERSIMMON = 0xc0ea
#     PEWTER_BLUE = 0x568d
#     PHLOX = 0x1fd8
#     PHTHALO_BLUE = 0x7100
#     PHTHALO_GREEN = 0xa411
#     PICOTEE_BLUE = 0x3029
#     PICTORIAL_CARMINE = 0x49c0
#     PIGGY_PINK = 0xfcfe
#     PINE_GREEN = 0xcd03
#     PINE_TREE = 0x6429
    PINK = 0x19fe
#     PINK_PANTONE = 0x52d2
#     PINK_FLAMINGO = 0xbffb
#     PINK_LACE = 0xfefe
#     PINK_LAVENDER = 0x9add
#     PINK_SHERBET = 0x74f4
#     PISTACHIO = 0x2e96
#     PLATINUM = 0x3ce7
#     PLUM = 0x308a
#     PLUM_WEB = 0x1bdd
#     PLUMP_PURPLE = 0x365a
#     POLISHED_PINE = 0x325d
#     POMP_AND_POWER = 0x1183
#     POPSTAR = 0x6cba
#     PORTLAND_ORANGE = 0xc6fa
#     POWDER_BLUE = 0x1cb7
#     PRINCETON_ORANGE = 0x04f4
#     PROCESS_YELLOW = 0x60ff
#     PRUNE = 0xe370
#     PRUSSIAN_BLUE = 0x8a01
#     PSYCHEDELIC_PURPLE = 0x1fd8
#     PUCE = 0x53cc
#     PULLMAN_BROWN_UPS_BROWN = 0x0262
#     PUMPKIN = 0xa3fb
#     PURPLE = 0x7568
#     PURPLE_WEB = 0x1080
#     PURPLE_MUNSELL = 0x1898
#     PURPLE_X11 = 0x1ea1
#     PURPLE_MOUNTAIN_MAJESTY = 0xd693
#     PURPLE_NAVY = 0x904a
#     PURPLE_PIZZAZZ = 0x7bfa
#     PURPLE_PLUM = 0x969a
#     PURPUREUS = 0x759a
#     QUEEN_BLUE = 0x5243
#     QUEEN_PINK = 0x7aee
#     QUICK_SILVER = 0x34a5
#     QUINACRIDONE_MAGENTA = 0xcb89
#     RADICAL_RED = 0xabf9
#     RAISIN_BLACK = 0x0421
#     RAJAH = 0x4cfd
#     RASPBERRY = 0x4be0
#     RASPBERRY_GLACE = 0xed92
#     RASPBERRY_ROSE = 0x2db2
#     RAW_SIENNA = 0x4bd4
#     RAW_UMBER = 0x2883
#     RAZZLE_DAZZLE_ROSE = 0x99f9
#     RAZZMATAZZ = 0x2de1
#     RAZZMIC_BERRY = 0x708a
#     REBECCA_PURPLE = 0x9361
    RED = 0x00f8
#     RED_CRAYOLA = 0x09e9
#     RED_MUNSELL = 0x07f0
#     RED_NCS = 0x06c0
#     RED_PANTONE = 0x47e9
#     RED_PIGMENT = 0xe4e8
#     RED_RYB = 0x22f9
#     RED_ORANGE = 0x89fa
#     RED_ORANGE_CRAYOLA = 0x43fb
#     RED_ORANGE_COLOR_WHEEL = 0x20fa
#     RED_PURPLE = 0x0fe0
#     RED_SALSA = 0xc9f9
#     RED_VIOLET = 0xb0c0
#     RED_VIOLET_CRAYOLA = 0x31c2
#     RED_VIOLET_COLOR_WHEEL = 0x4791
#     REDWOOD = 0xcaa2
#     RESOLUTION_BLUE = 0x1001
#     RHYTHM = 0xb273
#     RICH_BLACK = 0x0802
#     RICH_BLACK_FOGRA29 = 0x4200
#     RICH_BLACK_FOGRA39 = 0x0000
#     RIFLE_GREEN = 0x6742
#     ROBIN_EGG_BLUE = 0x7906
#     ROCKET_METALLIC = 0xf08b
#     ROJO_SPANISH_RED = 0x80a8
#     ROMAN_SILVER = 0x5284
#     ROSE = 0x0ff8
#     ROSE_BONBON = 0x13fa
#     ROSE_DUST = 0xed9a
#     ROSE_EBONY = 0x4862
#     ROSE_MADDER = 0x26e1
#     ROSE_PINK = 0x39fb
#     ROSE_POMPADOUR = 0xd3eb
#     ROSE_QUARTZ = 0xd5ac
#     ROSE_RED = 0xeac0
#     ROSE_TAUPE = 0xeb92
#     ROSE_VALE = 0x6aaa
#     ROSEWOOD = 0x0160
#     ROSSO_CORSA = 0x00d0
#     ROSY_BROWN = 0x71bc
#     ROYAL_BLUE_DARK = 0x0c01
#     ROYAL_BLUE_LIGHT = 0x5c43
#     ROYAL_PURPLE = 0x957a
#     ROYAL_YELLOW = 0xcbfe
#     RUBER = 0x2eca
#     RUBINE_RED = 0x0ad0
#     RUBY = 0x8be0
#     RUBY_RED = 0x8398
#     RUFOUS = 0xe0a8
#     RUSSET = 0x2382
#     RUSSIAN_GREEN = 0x8c64
#     RUSSIAN_VIOLET = 0xa930
#     RUST = 0x01b2
#     RUSTY_RED = 0x68d9
#     SACRAMENTO_STATE_GREEN = 0xc401
#     SADDLE_BROWN = 0x228a
#     SAFETY_ORANGE = 0xc0fb
#     SAFETY_ORANGE_BLAZE_ORANGE = 0x20fb
#     SAFETY_YELLOW = 0x80ee
#     SAFFRON = 0x26f6
#     SAGE = 0xd1bd
#     ST_PATRICK_S_BLUE = 0x4f21
#     SALMON = 0x0efc
#     SALMON_PINK = 0x94fc
#     SAND = 0x90c5
#     SAND_DUNE = 0x8293
#     SANDY_BROWN = 0x2cf5
#     SAP_GREEN = 0xe553
#     SAPPHIRE = 0x970a
#     SAPPHIRE_BLUE = 0x3403
#     SAPPHIRE_CRAYOLA = 0x3403
#     SATIN_SHEEN_GOLD = 0x06cd
#     SCARLET = 0x20f9
#     SCHAUSS_PINK = 0x95fc
#     SCHOOL_BUS_YELLOW = 0xc0fe
#     SCREAMIN__GREEN = 0xec67
#     SEA_GREEN = 0x4a2c
#     SEA_GREEN_CRAYOLA = 0xf907
#     SEAL_BROWN = 0x2159
#     SEASHELL = 0xbdff
#     SELECTIVE_YELLOW = 0xc0fd
#     SEPIA = 0x0272
#     SHADOW = 0xcb8b
#     SHADOW_BLUE = 0x5474
#     SHAMROCK_GREEN = 0xec04
#     SHEEN_GREEN = 0xa08e
#     SHIMMERING_BLUSH = 0x32dc
#     SHINY_SHAMROCK = 0x2f5d
#     SHOCKING_PINK = 0x78f8
#     SHOCKING_PINK_CRAYOLA = 0x7ffb
#     SIENNA = 0x6289
    SILVER = 0x18c6
#     SILVER_CRAYOLA = 0x17ce
#     SILVER_METALLIC = 0x55ad
#     SILVER_CHALICE = 0x75ad
#     SILVER_PINK = 0x75c5
#     SILVER_SAND = 0x18be
#     SINOPIA = 0x01ca
#     SIZZLING_RED = 0xcaf9
#     SIZZLING_SUNRISE = 0xc0fe
#     SKOBELOFF = 0xae03
#     SKY_BLUE = 0x7d86
#     SKY_BLUE_CRAYOLA = 0xbd76
#     SKY_MAGENTA = 0x95cb
#     SLATE_BLUE = 0xd96a
#     SLATE_GRAY = 0x1274
#     SLIMY_GREEN = 0xa22c
#     SMITTEN = 0x10ca
#     SMOKY_BLACK = 0x6110
#     SNOW = 0xdfff
#     SOLID_PINK = 0xc889
#     SONIC_SILVER = 0xae73
#     SPACE_CADET = 0x4a19
#     SPANISH_BISTRE = 0xa683
#     SPANISH_BLUE = 0x9703
#     SPANISH_CARMINE = 0x08d0
#     SPANISH_GRAY = 0xd39c
#     SPANISH_GREEN = 0x8a04
#     SPANISH_ORANGE = 0x00eb
#     SPANISH_PINK = 0xf7f5
#     SPANISH_RED = 0x04e0
#     SPANISH_SKY_BLUE = 0xff07
#     SPANISH_VIOLET = 0x5049
#     SPANISH_VIRIDIAN = 0xeb03
#     SPRING_BUD = 0xe0a7
#     SPRING_FROST = 0xe587
#     SPRING_GREEN = 0xef07
#     SPRING_GREEN_CRAYOLA = 0x57ef
#     STAR_COMMAND_BLUE = 0xd703
#     STEEL_BLUE = 0x1644
#     STEEL_PINK = 0x99c9
#     STEEL_TEAL = 0x515c
#     STIL_DE_GRAIN_YELLOW = 0xcbfe
#     STRAW = 0xcde6
#     STRAWBERRY = 0x8afa
#     STRAWBERRY_BLONDE = 0x8cfc
#     SUGAR_PLUM = 0x6e92
#     SUNGLOW = 0x66fe
#     SUNRAY = 0x4ae5
#     SUNSET = 0xb4fe
#     SUPER_PINK = 0x55cb
#     SWEET_BROWN = 0xa6a9
#     SYRACUSE_ORANGE = 0x20d2
#     TAN = 0xb1d5
#     TAN_CRAYOLA = 0xcddc
#     TANGERINE = 0x20f4
#     TANGO_PINK = 0x8fe3
#     TART_ORANGE = 0x68fa
#     TAUPE = 0xe649
#     TAUPE_GRAY = 0x318c
#     TEA_GREEN = 0x98d7
#     TEA_ROSE = 0x0ffc
#     TEA_ROSE = 0x18f6
#     TEAL = 0x1004
#     TEAL_BLUE = 0xb133
#     TELEMAGENTA = 0xaec9
#     TENNE_TAWNY = 0xa0ca
#     TERRA_COTTA = 0x8be3
#     THISTLE = 0xfbdd
#     THULIAN_PINK = 0x74db
#     TICKLE_ME_PINK = 0x55fc
#     TIFFANY_BLUE = 0xd60d
#     TIMBERWOLF = 0xbade
#     TITANIUM_YELLOW = 0x20ef
#     TOMATO = 0x08fb
#     TROPICAL_RAINFOREST = 0xab03
#     TRUE_BLUE = 0x582b
#     TRYPAN_BLUE = 0x3618
#     TUFTS_BLUE = 0x7b3c
#     TUMBLEWEED = 0x51dd
#     TURQUOISE = 0x1a47
#     TURQUOISE_BLUE = 0xfd07
#     TURQUOISE_GREEN = 0xb6a6
#     TURTLE_GREEN = 0xcb8c
#     TUSCAN = 0xb4fe
#     TUSCAN_BROWN = 0x666a
#     TUSCAN_RED = 0x497a
#     TUSCAN_TAN = 0xcba3
#     TUSCANY = 0xd3c4
#     TWILIGHT_LAVENDER = 0x4d8a
#     TYRIAN_PURPLE = 0x0760
#     UA_BLUE = 0x9501
#     UA_RED = 0x09d8
#     ULTRAMARINE = 0x1f38
#     ULTRAMARINE_BLUE = 0x3e43
#     ULTRA_PINK = 0x7ffb
#     ULTRA_RED = 0x70fb
#     UMBER = 0x8862
#     UNBLEACHED_SILK = 0xf9fe
    UNITED_NATIONS_BLUE = 0x9c5c
#     UNIVERSITY_OF_PENNSYLVANIA_RED = 0x04a0
#     UNMELLOW_YELLOW = 0xecff
#     UP_FOREST_GREEN = 0x2402
#     UP_MAROON = 0x8278
#     UPSDELL_RED = 0x05a9
#     URANIAN_BLUE = 0xdeae
#     USAFA_BLUE = 0x7302
#     VAN_DYKE_BROWN = 0x0562
#     VANILLA = 0x35f7
#     VANILLA_ICE = 0x75f4
#     VEGAS_GOLD = 0x8bc5
#     VENETIAN_RED = 0x42c8
#     VERDIGRIS = 0x9545
#     VERMILION = 0x06e2
#     VERMILION = 0xc3d9
#     VERONICA = 0x1ea1
#     VIOLET = 0x1f88
#     VIOLET_COLOR_WHEEL = 0x1f78
#     VIOLET_CRAYOLA = 0xef91
#     VIOLET_RYB = 0x1580
#     VIOLET_WEB = 0x1dec
#     VIOLET_BLUE = 0x5632
#     VIOLET_BLUE_CRAYOLA = 0x7973
#     VIOLET_RED = 0x92f2
#     VIRIDIAN = 0x0d44
#     VIRIDIAN_GREEN = 0xb304
#     VIVID_BURGUNDY = 0xe698
#     VIVID_SKY_BLUE = 0x7f06
#     VIVID_TANGERINE = 0x11fd
#     VIVID_VIOLET = 0x1f98
#     VOLT = 0xe0cf
#     WARM_BLACK = 0x0802
#     WHEAT = 0xf6f6
    WHITE = 0xffff
#     WILD_BLUE_YONDER = 0x7aa5
#     WILD_ORCHID = 0x94d3
#     WILD_STRAWBERRY = 0x14fa
#     WILD_WATERMELON = 0x70fb
#     WINDSOR_TAN = 0xa0a2
#     WINE = 0x6671
#     WINE_DREGS = 0x8861
#     WINTER_SKY = 0x0ff8
#     WINTERGREEN_DREAM = 0x4f54
#     WISTERIA = 0x1bcd
#     WOOD_BROWN = 0xcdc4
#     XANADU = 0x2f74
#     XANTHIC = 0x61ef
#     XANTHOUS = 0xa5f5
#     YALE_BLUE = 0xad01
    YELLOW = 0xe0ff
#     YELLOW_CRAYOLA = 0x50ff
#     YELLOW_MUNSELL = 0x60ee
#     YELLOW_NCS = 0x80fe
#     YELLOW_PANTONE = 0xe0fe
#     YELLOW_PROCESS = 0x60ff
#     YELLOW_RYB = 0xe6ff
#     YELLOW_GREEN = 0x669e
#     YELLOW_GREEN_CRAYOLA = 0x10c7
#     YELLOW_GREEN_COLOR_WHEEL = 0x8335
#     YELLOW_ORANGE = 0x68fd
#     YELLOW_ORANGE_COLOR_WHEEL = 0xa0fc
#     YELLOW_SUNSHINE = 0xa0ff
#     YINMN_BLUE = 0x922a
#     ZAFFRE = 0xb500
#     ZOMP = 0x313d

