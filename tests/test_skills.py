def test_skills_hierarchy(client, auth_headers):
    # 1. Create skill category
    res_cat = client.post('/api/v1/skills/categories', headers=auth_headers, json={
        'name': 'Cloud Architecture',
        'color_theme': 'cyan',
        'icon': 'fa-server'
    })
    assert res_cat.status_code == 201
    cat_id = res_cat.get_json()['category']['id']

    # 2. Add module to category with string category_id (as submitted by browser form)
    res_mod = client.post('/api/v1/skills/modules', headers=auth_headers, json={
        'category_id': str(cat_id),
        'title': 'Terraform Infrastructure'
    })
    assert res_mod.status_code == 201
    mod_id = res_mod.get_json()['module']['id']

    # Test invalid category_id returns 400
    res_invalid = client.post('/api/v1/skills/modules', headers=auth_headers, json={
        'category_id': 'invalid_string',
        'title': 'Failing Module'
    })
    assert res_invalid.status_code == 400

    # Test non-existent category_id returns 404
    res_missing = client.post('/api/v1/skills/modules', headers=auth_headers, json={
        'category_id': 99999,
        'title': 'Missing Module'
    })
    assert res_missing.status_code == 404

    # 3. Add metric log to module with string module_id (as submitted by browser form)
    res_log = client.post('/api/v1/skills/logs', headers=auth_headers, json={
        'module_id': str(mod_id),
        'name': 'AWS VPC Module',
        'metric': 'Production Ready'
    })
    assert res_log.status_code == 201
    assert res_log.get_json()['user_xp'] == 110  # 100 + 10 XP

    # 4. Fetch skills and verify structure
    res_get = client.get('/api/v1/skills', headers=auth_headers)
    assert res_get.status_code == 200
    categories = res_get.get_json()['categories']
    found = any(c['id'] == cat_id for c in categories)
    assert found is True

def test_notes_save_and_retrieve(client, auth_headers):
    # Save note
    res_save = client.post('/api/v1/notes', headers=auth_headers, json={
        'content': 'Focused morning work block completed.'
    })
    assert res_save.status_code == 200
    assert res_save.get_json()['success'] is True

    # Retrieve note
    res_get = client.get('/api/v1/notes', headers=auth_headers)
    assert res_get.status_code == 200
    assert res_get.get_json()['note']['content'] == 'Focused morning work block completed.'
