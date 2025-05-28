import json

def update_json_keys():
    # 读取原始JSON文件
    with open('all_courses.json', 'r', encoding='utf-8') as f:
        courses = json.load(f)
    
    # 更新每个课程的上课时间键名
    for course in courses:
        for time_slot in course['上课时间']:
            # 创建新的键值对
            time_slot['weekday'] = time_slot.pop('周几')
            time_slot['period'] = time_slot.pop('节数')
    
    # 将更新后的数据写回文件
    with open('all_courses.json', 'w', encoding='utf-8') as f:
        json.dump(courses, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    update_json_keys()
    print("JSON文件更新完成！") 