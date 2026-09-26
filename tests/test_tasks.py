def test_create_and_toggle_daily_task(client, auth_headers):
    # 1. Create task
    res = client.post('/api/v1/tasks', headers=auth_headers, json={
        'title': 'Test Daily Objective',
        'priority': 'high',
        'category': 'Testing'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    task_id = data['task']['id']
    assert data['task']['title'] == 'Test Daily Objective'
    assert data['task']['completed'] is False

    # 2. Toggle task
    res_toggle = client.post(f'/api/v1/tasks/{task_id}/toggle', headers=auth_headers)
    assert res_toggle.status_code == 200
    toggle_data = res_toggle.get_json()
    assert toggle_data['success'] is True
    assert toggle_data['completed'] is True
    # Initial 100 XP + 15 XP = 115 XP
    assert toggle_data['user_xp'] == 115

    # 3. Delete task
    res_del = client.delete(f'/api/v1/tasks/{task_id}', headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.get_json()['success'] is True

def test_weekly_milestones(client, auth_headers):
    # Create weekly goal
    res = client.post('/api/v1/tasks/weekly', headers=auth_headers, json={
        'title': 'Achieve 100% test coverage'
    })
    assert res.status_code == 201
    goal_id = res.get_json()['weekly_task']['id']

    # Toggle weekly goal
    res_toggle = client.post(f'/api/v1/tasks/weekly/{goal_id}/toggle', headers=auth_headers)
    assert res_toggle.status_code == 200
    assert res_toggle.get_json()['completed'] is True
    assert res_toggle.get_json()['user_xp'] == 130  # 100 + 30 XP

    # Delete weekly goal
    res_del = client.delete(f'/api/v1/tasks/weekly/{goal_id}', headers=auth_headers)
    assert res_del.status_code == 200
