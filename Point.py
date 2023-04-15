class Point:
    """
    param x: the axis x
    param y: the axis y
    param z: the axis z
    param qx: the quaternion x
    param qy: the quaternion y
    param qz: the quaternion z
    param qw: the quaternion w
    param frame_id: in order gather all the frame points in a points list
    param label: in order to find clusters
    """
    def __init__(self, x, y, z, qx=0.0, qy=0.0, qz=0.0, qw=0.0, frame_id=0, label=-1):
        self.x = x
        self.y = y
        self.z = z
        self.qx = qx
        self.qy = qy
        self.qz = qz
        self.qw = qw
        self.label = label
        self.frame_id = frame_id

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def copy(self):
        return Point(self.x, self.y, self.z, self.qx, self.qy, self.qz, self.qw, self.frame_id, self.label)
