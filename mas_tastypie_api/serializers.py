from tastypie.serializers import Serializer as TSerializer
from mas_tastypie_api.http import Result


class Serializer(TSerializer):
    """
    """
    pass
    # def to_json(self, data, options=None):
    #     """
    #     Given some Python data, produces JSON output.
    #     """
    #     options = options or {}
    #     data = self.to_simple(data, options)
    #
    #     # return djangojson.json.dumps(data, cls=djangojson.DjangoJSONEncoder,
    #     #     sort_keys=True, ensure_ascii=False)
    #     print "hahahha"
    #     import pdb;pdb.set_trace()
    #     return Result(data=data)
