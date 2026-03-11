class Vec2:
    def __init__(self, x:int, y:int):
        self.set_val(x,y)
        
    def get_x(self) -> int:
        return self.__x
    
    
    def get_y(self) -> int:
        return self.__y
        
    def add(self, other: Vec2) -> None:
        self.__x += other.get_x()
        self.__y += other.get_y()
        
    def set_val(self, x, y) -> None:
        self.__x = x
        self.__y = y
        
        
VEC_DOWN = Vec2(0,1)
VEC_UP = Vec2(0,-1)
VEC_RIGHT = Vec2(1,0)
VEC_LEFT = Vec2(-1,0)