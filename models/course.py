from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class CourseTime:
    """课程时间模型"""
    weekday: str  # 周几
    period: str  # 节数

@dataclass
class Course:
    """课程模型"""
    name: str  # 课程名称
    credits: int  # 学分
    times: List[CourseTime]  # 上课时间
    prerequisites: List[str]  # 先修课程
    description: str  # 课程介绍
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Course':
        """从字典创建课程对象"""
        times = [CourseTime(**time) for time in data['上课时间']]
        prerequisites = data['先修课程'] if isinstance(data['先修课程'], list) else [data['先修课程']]
        if prerequisites[0] == '无':
            prerequisites = []
        return cls(
            name=data['课程名'],
            credits=data['学分'],
            times=times,
            prerequisites=prerequisites,
            description=data['课程介绍']
        )
    
    def has_time_conflict(self, other: 'Course') -> bool:
        """检查与另一门课程是否有时间冲突"""
        for time1 in self.times:
            for time2 in other.times:
                if time1.weekday == time2.weekday:
                    # 解析节数并检查是否有重叠
                    periods1 = [int(x) for x in time1.period.split('-')]
                    periods2 = [int(x) for x in time2.period.split('-')]
                    if not (periods1[1] < periods2[0] or periods2[1] < periods1[0]):
                        return True
        return False 