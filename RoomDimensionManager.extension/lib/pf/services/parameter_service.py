try:
    from Autodesk.Revit.DB import StorageType, ElementId
except ImportError:
    class StorageType(object):
        String = "String"
        Double = "Double"
        Integer = "Integer"
        ElementId = "ElementId"
    class ElementId(object):
        InvalidElementId = -1
        def __init__(self, val=-1): self.IntegerValue = val
from pf.services.cache_service import PFCacheService

class ParameterMetadata(object):
    def __init__(self, name, storage_type=StorageType.String, is_readonly=False, is_shared=False, is_builtin=False, is_instance=True, is_type=False, guid=""):
        self.name = name
        self.storage_type = storage_type
        self.is_readonly = is_readonly
        self.is_shared = is_shared
        self.is_builtin = is_builtin
        self.is_instance = is_instance
        self.is_type = is_type
        self.guid = guid

class PFParameterService(object):
    def __init__(self, doc):
        self.doc = doc

    def discover_parameters_for_elements(self, elements, cat_key=None):
        """Discovers Instance + Type parameters for elements, returns sorted parameter names."""
        if cat_key:
            cached = PFCacheService.get_parameters(cat_key)
            if cached is not None:
                return cached

        meta_map = {}
        for elem in elements[:50]:  # Inspect first 50 elements for speed
            try:
                # 1. Instance Parameters
                for p in elem.Parameters:
                    try:
                        if p.Definition and p.Definition.Name and p.Definition.Name not in meta_map:
                            guid_str = str(p.GUID) if hasattr(p, 'IsShared') and p.IsShared and hasattr(p, 'GUID') else ""
                            meta = ParameterMetadata(
                                name=p.Definition.Name,
                                storage_type=p.StorageType,
                                is_readonly=p.IsReadOnly,
                                is_shared=getattr(p, 'IsShared', False),
                                is_builtin=not getattr(p, 'IsShared', False),
                                is_instance=True,
                                is_type=False,
                                guid=guid_str
                            )
                            meta_map[p.Definition.Name] = meta
                    except Exception:
                        pass

                # 2. Type Parameters
                try:
                    elem_type_id = elem.GetTypeId()
                    if elem_type_id and elem_type_id != ElementId.InvalidElementId:
                        elem_type = self.doc.GetElement(elem_type_id)
                        if elem_type:
                            for tp in elem_type.Parameters:
                                if tp.Definition and tp.Definition.Name and tp.Definition.Name not in meta_map:
                                    guid_str = str(tp.GUID) if hasattr(tp, 'IsShared') and tp.IsShared and hasattr(tp, 'GUID') else ""
                                    meta = ParameterMetadata(
                                        name=tp.Definition.Name,
                                        storage_type=tp.StorageType,
                                        is_readonly=tp.IsReadOnly,
                                        is_shared=getattr(tp, 'IsShared', False),
                                        is_builtin=not getattr(tp, 'IsShared', False),
                                        is_instance=False,
                                        is_type=True,
                                        guid=guid_str
                                    )
                                    meta_map[tp.Definition.Name] = meta
                except Exception:
                    pass
            except Exception:
                pass

        result_names = sorted(meta_map.keys())
        if cat_key:
            PFCacheService.set_parameters(cat_key, result_names)
        return result_names
