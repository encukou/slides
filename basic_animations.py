import random

async def anim_blink(blinky):
    await blinky.show_face('(-.-)', 0.1)


async def anim_blink2(blinky):
    await blinky.show_face('(-.-)', 0.1)
    await blinky.show_face('(o.o)', 0.1)
    await blinky.show_face('(-.-)', 0.1)


async def anim_wink(blinky):
    await blinky.show_face('(-.o)', 0.1)


async def anim_wink_alt(blinky):
    await blinky.show_face('(o.-)', 0.1)


async def anim_wink2(blinky):
    await blinky.show_face('(-.o)', 0.1)
    await blinky.show_face('(o.o)', 0.1)
    await blinky.show_face('(-.o)', 0.1)


async def anim_wink2_alt(blinky):
    await blinky.show_face('(o.-)', 0.1)
    await blinky.show_face('(o.o)', 0.1)
    await blinky.show_face('(o.-)', 0.1)


async def anim_eyebrows(blinky):
    await blinky.show_face('(ô_ô)', 0.8)


async def anim_surprise(blinky):
    await blinky.show_face('(O.O)', 0.8)


async def anim_wide_mouth(blinky):
    await blinky.show_face('(o_o)', 0.8)


async def anim_blank(blinky):
    await blinky.show_face('(o.o)', 2)


async def anim_munch(blinky):
    for i in range(10):
        await blinky.show_face('(o_o)', 0.1)
        await blinky.show_face('(o.o)', 0.1)


async def anim_smile(blinky):
    await blinky.show_face('(o_o)', 0.1)
    await blinky.show_face('(^_^)', 0.5)
    await blinky.show_face('(o_o)', 0.1)


async def anim_look(blinky):
    for i in range(3):
        await blinky.show_face(' (o.O', 0.5)
        await blinky.show_face('(o.o)', 0.2)
        await blinky.show_face('O.o) ', 0.5)
        await blinky.show_face('(o.o)', 0.2)


async def anim_sleep(blinky):
    await blinky.show_face('(°.°)', 0.1)
    await blinky.show_face('(°o°)', 0.2)
    await blinky.show_face('(°O°)', 0.6)
    await blinky.show_face('(°o°)', 0.3)
    await blinky.show_face('(°.°)', 0.2)
    await blinky.show_face('(-.-)', random.uniform(2, 30))
    await blinky.show_face('(o.o)', 0.1)
    await anim_blink2(blinky)


###

all_animations = [
    func for name, func in globals().items()
    if name.startswith('anim_')
]

async def animation(blinky):
    try:
        func = random.choice(all_animations)
        await blinky.show_face('(o.o)', random.uniform(1, 1.5))
        await func(blinky)
    except:
        blinky.face = '(×.×)'
        raise
