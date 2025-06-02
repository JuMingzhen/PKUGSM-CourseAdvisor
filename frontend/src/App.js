import React, { useState } from 'react';

function App() {
  const [formData, setFormData] = useState({
    is_freshman: true,
    current_grade: 1,
    current_semester: 1,
    study_abroad: false,
    internship: false,
    internship_semester: null,
    completed_courses: [],
    planning_type: 'Minimal Effort',
    target_credits_per_semester: 15,
    preferred_subjects: [],
    upperbound_credits: 20
  });
  const [completedCoursesInput, setCompletedCoursesInput] = useState('');
  const [schedule, setSchedule] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const planningTypes = [
    { value: 'Minimal Effort', label: '最小努力型' },
    { value: 'Balanced Workload', label: '均衡发展型' },
    { value: 'Focused Depth', label: '专注深度型' },
    { value: 'Maximum Intensity', label: '最大强度型' }
  ];

  const subjectOptions = [
    { value: 'Corporate Finance', label: '公司金融' },
    { value: 'Investment', label: '投资学' },
    { value: 'Financial Markets', label: '金融市场' },
    { value: 'Financial Engineering', label: '金融工程' },
    { value: 'Financial Accounting', label: '财务会计' },
    { value: 'Management Accounting', label: '管理会计' },
    { value: 'Marketing', label: '市场营销' },
    { value: 'Strategy', label: '战略管理' },
    { value: 'Organization', label: '组织管理' }
  ];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : 
              name === 'internship_semester' ? (value ? parseInt(value) : null) :
              type === 'number' ? parseInt(value) : value
    }));
  };

  const handleSubjectChange = (e) => {
    const { value, checked } = e.target;
    setFormData(prev => {
      const subjects = checked 
        ? [...prev.preferred_subjects, value]
        : prev.preferred_subjects.filter(s => s !== value);
      return {
        ...prev,
        preferred_subjects: subjects.slice(0, 3) // 最多选择3个
      };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSchedule(null);
    setMessage('');
    try {
      // 处理已修课程，确保格式正确
      const completedCourses = completedCoursesInput
        .split(/[^\w\s]/)
        .map(s => s.trim())
        .filter(Boolean);

      console.log('已修课程列表:', completedCourses); // 调试信息

      // 确保所有数值类型正确
      const payload = {
        is_freshman: Boolean(formData.is_freshman),
        current_grade: formData.is_freshman ? 1 : parseInt(formData.current_grade),
        current_semester: formData.is_freshman ? 1 : parseInt(formData.current_semester),
        completed_courses: completedCourses,
        study_abroad: Boolean(formData.study_abroad),
        internship: Boolean(formData.internship),
        internship_semester: formData.internship ? parseInt(formData.internship_semester) : null,
        planning_type: String(formData.planning_type),
        target_credits_per_semester: formData.planning_type === 'Balanced Workload' ? 
          parseInt(formData.target_credits_per_semester) : null,
        preferred_subjects: Array.from(formData.preferred_subjects),
        upperbound_credits: parseInt(formData.upperbound_credits)
      };

      console.log('发送到后端的数据:', payload); // 调试信息

      const response = await fetch('http://localhost:5000/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      console.log('后端返回的数据:', data); // 调试信息
      
      if (data.error) {
        console.error('后端返回错误:', data.error);
        setError(data.error);
      } else {
        setSchedule(data.schedule);
        setMessage(data.message);
      }
    } catch (error) {
      console.error('请求错误:', error); // 调试信息
      setError('网络错误或服务器未启动');
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>光华管理学院金融系选课推荐系统</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            是否新生：
            <input
              type="checkbox"
              name="is_freshman"
              checked={formData.is_freshman}
              onChange={handleChange}
            />
          </label>
        </div>

        {!formData.is_freshman && (
          <>
            <div>
              <label>
                当前年级：
                <select
                  name="current_grade"
                  value={formData.current_grade}
                  onChange={handleChange}
                >
                  {[1, 2, 3, 4].map(grade => (
                    <option key={grade} value={grade}>
                      {grade}年级
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div>
              <label>
                当前学期：
                <select
                  name="current_semester"
                  value={formData.current_semester}
                  onChange={handleChange}
                >
                  <option value={1}>第1学期</option>
                  <option value={2}>第2学期</option>
                </select>
              </label>
            </div>

            <div>
              <label>
                已修课程（用逗号分隔）：
                <input
                  type="text"
                  name="completed_courses"
                  value={completedCoursesInput}
                  onChange={(e) => setCompletedCoursesInput(e.target.value)}
                />
              </label>
            </div>
          </>
        )}

        <div>
          <label>
            是否计划出国：
            <input
              type="checkbox"
              name="study_abroad"
              checked={formData.study_abroad}
              onChange={handleChange}
            />
          </label>
        </div>

        <div>
          <label>
            是否计划实习：
            <input
              type="checkbox"
              name="internship"
              checked={formData.internship}
              onChange={handleChange}
            />
          </label>
        </div>

        {formData.internship && (
          <div>
            <label>
              计划实习学期：
              <select
                name="internship_semester"
                value={formData.internship_semester || ''}
                onChange={handleChange}
              >
                <option value="">请选择</option>
                {[1, 2, 3, 4, 5, 6, 7, 8].map(semester => (
                  <option key={semester} value={semester}>
                    第{semester}学期
                  </option>
                ))}
              </select>
            </label>
          </div>
        )}

        <div>
          <label>
            整体规划类型：
            <select
              name="planning_type"
              value={formData.planning_type}
              onChange={handleChange}
            >
              {planningTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        {formData.planning_type === 'Balanced Workload' && (
          <div>
            <label>
              目标每学期学分：
              <input
                type="number"
                name="target_credits_per_semester"
                value={formData.target_credits_per_semester}
                onChange={handleChange}
                min="9"
                max="20"
              />
            </label>
          </div>
        )}

        <div>
          <label>
            每学期光华专业课学分上限（9-20）：
            <input
              type="number"
              name="upperbound_credits"
              value={formData.upperbound_credits}
              onChange={handleChange}
              min="9"
              max="20"
            />
          </label>
        </div>

        <div>
          <label>偏好学科（最多选择3个）：</label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
            {subjectOptions.map(subject => (
              <label key={subject.value}>
                <input
                  type="checkbox"
                  value={subject.value}
                  checked={formData.preferred_subjects.includes(subject.value)}
                  onChange={handleSubjectChange}
                  disabled={!formData.preferred_subjects.includes(subject.value) && formData.preferred_subjects.length >= 3}
                />
                {subject.label}
              </label>
            ))}
          </div>
        </div>

        <button type="submit">生成推荐课表</button>
      </form>

      {error && <div style={{ color: 'red' }}>{error}</div>}
      {message && <div style={{ color: 'blue', margin: '10px 0' }}>{message}</div>}

      {schedule && (
        <div>
          <h2>推荐课表</h2>
          {Object.entries(schedule).map(([semester, courses]) => (
            <div key={semester}>
              <h3>第{semester}学期</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>课程名称</th>
                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>学分</th>
                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>上课时间</th>
                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>教师</th>
                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>地点</th>
                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>备注</th>
                  </tr>
                </thead>
                <tbody>
                  {courses.map((course, index) => (
                    <tr key={index}>
                      <td style={{ border: '1px solid #ddd', padding: '8px' }}>{course.name}</td>
                      <td style={{ border: '1px solid #ddd', padding: '8px' }}>{course.credits}</td>
                      <td style={{ border: '1px solid #ddd', padding: '8px' }}>{course.time}</td>
                      <td style={{ border: '1px solid #ddd', padding: '8px' }}>{course.teacher}</td>
                      <td style={{ border: '1px solid #ddd', padding: '8px' }}>{course.location}</td>
                      <td style={{ border: '1px solid #ddd', padding: '8px' }}>{course.note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;