import random


class Philosopher:
    def __init__(self, family, async_library):
        self.face = ' (o.o) '
        self.family = family
        self.async_library = async_library
        self.left_fork = async_library.Lock()

    @property
    def right_neighbor(self):
        index = self.family.index(self)
        return self.family[(index + 1) % len(self.family)]

    def __str__(self):
        if self.left_fork.locked():
            fork = '_'
        else:
            fork = '⑂'
        return fork + ' ' + self.face

    async def run(self):
        while True:
            if random.randrange(2):
                forks = self.left_fork, self.right_neighbor.left_fork
                intermediate_faces = ' (O.o) ', '⑂(o.O) '
            else:
                forks = self.right_neighbor.left_fork, self.left_fork
                intermediate_faces = ' (o.O) ', ' (O.o)⑂'

            await self.show_face(intermediate_faces[0], 0)
            async with forks[0]:
                await self.show_face(intermediate_faces[1].replace(*'Oo'), 0.1)
                await self.show_face(intermediate_faces[1], 0)
                async with forks[1]:
                    for i in range(20):
                        await self.show_face('⑂(o.o)⑂', 0.1)
                        await self.show_face('⑂(o_o)⑂', 0.1)
                await self.show_face(intermediate_faces[1].replace(*'Oo'), 0.3)

            # Thinking
            await self.show_face(' (ô.ô) ', random.uniform(1, 3))

    async def show_face(self, new_face, delay):
        """Sets a new `face` string and keep it for `delay` seconds"""
        self.face = new_face
        print('\r', *self.family, end='\r')
        await self.async_library.sleep(delay)
