import React, { useState } from 'react';

function App() {
  const [form, setForm] = useState({
    is_freshman: false,
    current_grade: 1,
    current_semester: 1,
    completed_courses: '',
    study_abroad: false,
    internship: false,
    internship_semester: null
  });
  const [schedule, setSchedule] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({
      ...f,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setSchedule(null);
    setMessage('');
    const payload = {
      ...form,
      completed_courses: form.completed_courses.split(',').map(s => s.trim()).filter(Boolean)
    };
    try {
      const res = await fetch('http://localhost:5000/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.error) setError(data.error);
      else {
        setSchedule(data.schedule);
        setMessage(data.message);
      }
    } catch (e) {
      setError('网络错误或服务器未启动');
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>光华管理学院金融系选课推荐系统</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            <input
              type="checkbox"
              name="is_freshman"
              checked={form.is_freshman}
              onChange={handleChange}
            />
            我是新生
          </label>
        </div>

        {!form.is_freshman && (
          <>
            <div>
              <label>
                当前年级：
                <select
                  name="current_grade"
                  value={form.current_grade}
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
                  value={form.current_semester}
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
                  value={form.completed_courses}
                  onChange={handleChange}
                />
              </label>
            </div>
          </>
        )}

        <div>
          <label>
            <input
              type="checkbox"
              name="study_abroad"
              checked={form.study_abroad}
              onChange={handleChange}
            />
            计划出国留学
          </label>
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              name="internship"
              checked={form.internship}
              onChange={handleChange}
            />
            计划实习
          </label>
        </div>

        {form.internship && (
          <div>
            <label>
              实习学期：
              <select
                name="internship_semester"
                value={form.internship_semester || ''}
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

        <button type="submit">生成推荐课表</button>
      </form>

      {error && <div style={{ color: 'red' }}>{error}</div>}
      {message && <div style={{ color: 'blue', margin: '10px 0' }}>{message}</div>}

      {schedule && (
        <div>
          <h2>推荐课表</h2>
          {Object.keys(schedule).map(semester => (
            <div key={semester}>
              <h3>第{semester}学期</h3>
              <table border="1" cellPadding="6">
                <thead>
                  <tr>
                    <th>课程名</th>
                    <th>学分</th>
                    <th>时间</th>
                    <th>教师</th>
                    <th>地点</th>
                    <th>备注</th>
                  </tr>
                </thead>
                <tbody>
                  {schedule[semester].map((course, idx) => (
                    <tr key={idx}>
                      <td>{course.name}</td>
                      <td>{course.credits}</td>
                      <td>{course.time}</td>
                      <td>{course.teacher}</td>
                      <td>{course.location}</td>
                      <td>{course.note}</td>
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