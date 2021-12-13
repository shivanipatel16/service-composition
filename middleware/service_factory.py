_service_factory = {"menu": {"collections": {"product",
                                             "topping"},
                             "base_url": "http://f21cloudmenu-env.eba-fspbcfys.us-east-2.elasticbeanstalk.com"},
                    "login": {"collections": {"address",
                                              "users"},
                              "base_url": "http://3.144.211.3:5000"},
                    "order": {"collections": {"info",
                                              "orders"},
                              "base_url": "http://3.144.211.3:5000"}  # TODO
                    }


def get_service_factory_url(resource_service, resource_collection):
    if resource_service not in _service_factory:
        return None  # error
    elif resource_collection not in _service_factory[resource_service]["collections"]:
        return None  # error
    else:
        base_url = _service_factory[resource_service]["base_url"]
        #base_url = "http://160.39.156.166:5000"
        service_url = "{}/api/{}/{}".format(base_url, resource_service, resource_collection)
        return service_url


get_service_factory_url("menu", "product")
