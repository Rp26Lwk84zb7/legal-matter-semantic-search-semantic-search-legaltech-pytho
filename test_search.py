from main import choose_follow_up


def test_deadline_is_prioritized_for_matter_queue():
    results = [{"metadata": {"matter_id": "M-42", "signed": True, "deadline_days": 2}}]
    assert choose_follow_up(results) == {"action": "deadline_follow_up", "matter": "M-42"}
