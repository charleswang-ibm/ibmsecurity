import logging

logger = logging.getLogger(__name__)


def get_all(isamAppliance, check_mode=False, force=False):
    """
    Retrieve a list of point of contact profiles
    """
    return isamAppliance.invoke_get("Retrieve a list of point of contact profiles",
                                    "/iam/access/v8/poc/profiles/")


def get(isamAppliance, name, check_mode=False, force=False):
    """
    Retrieve a list of point of contact profiles
    """
    ret_obj = search(isamAppliance, name=name, check_mode=check_mode, force=force)
    poc_id = ret_obj['data']

    if poc_id == {}:
        return isamAppliance.create_return_object()
    else:
        return _get(isamAppliance, poc_id)


def _get(isamAppliance, id):
    return isamAppliance.invoke_get("Retrieve a list of point of contact profiles",
                                    "/iam/access/v8/poc/profiles/{0}".format(id))


def get_currentID(isamAppliance, check_mode=False, force=False):
    """
    Retrieve the current point of contact profile information
    """
    return isamAppliance.invoke_get("Retrieve the current point of contact profile information",
                                    "/iam/access/v8/poc/")


def set_current(isamAppliance, name, check_mode=False, force=False):
    """
    Update the current point of contact profile information
    """
    ret_obj = search(isamAppliance, name=name, check_mode=check_mode, force=force)
    poc_id = ret_obj['data']
    logger.debug("POC ID to be set Current: {0}".format(poc_id))

    if force is False:
        ret_obj = get_currentID(isamAppliance)
        cur_poc_id = ret_obj['data']['currentProfileId']
        logger.debug("Current POC ID is: {0}".format(cur_poc_id))

    if force is True or poc_id != cur_poc_id:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True)
        else:
            return isamAppliance.invoke_put(
                "Update the current point of contact profile information",
                "/iam/access/v8/poc",
                {
                    "currentProfileId": poc_id
                })

    return isamAppliance.create_return_object()


def set(isamAppliance, name, description=None, authenticateCallbacks=None, signInCallbacks=None, localIdCallbacks=None,
        signOutCallbacks=None, authnPolicyCallbacks=None, check_mode=False, force=False):
    """
    Creating or Modifying a POC Profile
    """
    if (search(isamAppliance, name=name))['data'] == {}:
        logger.debug("Adding a new POC Profile")
        # Force the add - we already know federation does not exist
        return add(isamAppliance, name, description, authenticateCallbacks, signInCallbacks, localIdCallbacks,
                   signOutCallbacks, authnPolicyCallbacks, check_mode, True)
    else:
        logger.debug("Updating existing POC Profile")
        # Update request
        return update(isamAppliance, name, description, authenticateCallbacks, signInCallbacks, localIdCallbacks,
                      signOutCallbacks, authnPolicyCallbacks, check_mode, force)


def add(isamAppliance, name, description=None, authenticateCallbacks=None, signInCallbacks=None, localIdCallbacks=None,
        signOutCallbacks=None, authnPolicyCallbacks=None, check_mode=False, force=False):
    """
    Create a new point of contact profile
    """
    if force is False:
        ret_obj = search(isamAppliance, name)

    if force is True or ret_obj['data'] == {}:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True)
        else:
            json_data = _create_json(name, description, authenticateCallbacks, signInCallbacks, localIdCallbacks,
                                     signOutCallbacks, authnPolicyCallbacks)

            return isamAppliance.invoke_post(
                "Create a new point of contact profile",
                "/iam/access/v8/poc/profiles/", json_data)

    return isamAppliance.create_return_object()


def update(isamAppliance, name, description=None, authenticateCallbacks=None, signInCallbacks=None,
           localIdCallbacks=None, signOutCallbacks=None, authnPolicyCallbacks=None, check_mode=False, force=False):
    """
    Update a specific point of contact profile
    """
    update_required, poc_id = _check(isamAppliance, name, description, authenticateCallbacks, signInCallbacks,
                                     localIdCallbacks, signOutCallbacks, authnPolicyCallbacks)

    if force is True or update_required is True:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True)
        else:
            json_data = _create_json(name, description, authenticateCallbacks, signInCallbacks, localIdCallbacks,
                                     signOutCallbacks, authnPolicyCallbacks)
            return isamAppliance.invoke_put(
                "Update a specific point of contact profile",
                "/iam/access/v8/poc/profiles/{0}".format(poc_id), json_data)

    return isamAppliance.create_return_object()


def delete(isamAppliance, name, check_mode=False, force=False):
    """
    Delete a point of contact profile
    """
    ret_obj = search(isamAppliance, name, check_mode=check_mode, force=force)

    if force is True or ret_obj['data'] != {}:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True)
        else:
            poc_id = ret_obj['data']
            return isamAppliance.invoke_delete(
                "Delete a point of contact profile",
                "/iam/access/v8/poc/profiles/{0}".format(poc_id))

    return isamAppliance.create_return_object()


def search(isamAppliance, name, force=False, check_mode=False):
    """
    Search Point Of Contact Profile by name
    """
    ret_obj = get_all(isamAppliance)
    return_obj = isamAppliance.create_return_object()

    for obj in ret_obj['data']:
        if obj['name'] == name:
            logger.debug("Matched on name: {0}, ID: {1}".format(name, obj['id']))
            return_obj['data'] = obj['id']

    return return_obj


def _check(isamAppliance, name, description, authenticateCallbacks, signInCallbacks, localIdCallbacks, signOutCallbacks,
           authnPolicyCallbacks):
    """
    Check and return True if update needed
    """
    update_required = False
    poc_id = None
    ret_obj = get(isamAppliance, name)

    if ret_obj['data'] != {}:
        json_data = _create_json(name, description, authenticateCallbacks, signInCallbacks, localIdCallbacks,
                                 signOutCallbacks, authnPolicyCallbacks)
        poc_id = ret_obj['data']['id']
        del ret_obj['data']['id']
        del ret_obj['data']['isReadOnly']
        logger.debug("Current POC Data: {0}".format(ret_obj['data']))
        logger.debug("POC Data to update: {0}".format(json_data))
        import ibmsecurity.utilities.tools
        if ibmsecurity.utilities.tools.json_sort(ret_obj['data']) != ibmsecurity.utilities.tools.json_sort(json_data):
            update_required = True

    return update_required, poc_id


def _create_json(name, description=None, authenticateCallbacks=None, signInCallbacks=None, localIdCallbacks=None,
                 signOutCallbacks=None, authnPolicyCallbacks=None):
    json_data = {
        "name": name
    }
    if description is not None:
        json_data['description'] = description
    if authenticateCallbacks is not None:
        json_data['authenticateCallbacks'] = authenticateCallbacks
    if signInCallbacks is not None:
        json_data['signInCallbacks'] = signInCallbacks
    if localIdCallbacks is not None:
        json_data['localIdCallbacks'] = localIdCallbacks
    if signOutCallbacks is not None:
        json_data['signOutCallbacks'] = signOutCallbacks
    if authnPolicyCallbacks is not None:
        json_data['authnPolicyCallbacks'] = authnPolicyCallbacks

    return json_data


def compare(isamAppliance1, isamAppliance2):
    """
    Compare Point of Contact profiles between two appliances
    """
    ret_obj1 = get_all(isamAppliance1)
    ret_obj2 = get_all(isamAppliance2)

    for obj in ret_obj1['data']:
        del obj['id']
    for obj in ret_obj2['data']:
        del obj['id']

    import ibmsecurity.utilities.tools
    return ibmsecurity.utilities.tools.json_compare(ret_obj1, ret_obj2, deleted_keys=['id'])
