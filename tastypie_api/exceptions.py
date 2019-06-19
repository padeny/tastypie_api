

class DataFormatError(Exception):
    """
        raise the error when data format is incorrect,and except it in
        post_list;
    """
    def __init__(self, msg=u"data format error!"):
        self.msg = msg
