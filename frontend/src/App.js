import React, { useState } from 'react';
import './App.css';

function App() {
    const [formData, setFormData] = useState({
        is_freshman: true,
        current_grade: '',
        current_semester: '',
        completed_courses: '',
        study_abroad: false,
        internship: false,
        internship_semester: '',
        planning_type: 'Minimal Effort',
        target_credits_per_semester: '',
        preferred_subjects: [],
        upperbound_credits: 20
    });

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const planningTypes = {
        'Minimal Effort': '轻松过关',
        'Balanced Workload': '适度均衡',
        'Focused Depth': '专注深化',
        'Maximum Intensity': '极限挑战'
    };

    const subjectOptions = [
        '量化金融与金融工程',
        '数理研究',
        '投资与资产管理',
        '财务分析',
        '宏观金融与经济政策',
        '金融经济学',
        '组织管理',
        '市场营销',
        '中国经济社会研究'
    ];

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubjectToggle = (subject) => {
        setFormData(prev => {
            const subjects = [...prev.preferred_subjects];
            const index = subjects.indexOf(subject);
            if (index === -1 && subjects.length < 3) {
                subjects.push(subject);
            } else if (index !== -1) {
                subjects.splice(index, 1);
            }
            return { ...prev, preferred_subjects: subjects };
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResult(null);

        try {
            const response = await fetch('http://localhost:5000/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || '请求失败');
            }
            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <h1>光华管理学院金融系选课推荐系统</h1>

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>
                        <input
                            type="checkbox"
                            name="is_freshman"
                            checked={formData.is_freshman}
                            onChange={handleInputChange}
                        />
                        是否为新生
                    </label>
                </div>

                {!formData.is_freshman && (
                    <>
                        <div className="form-group">
                            <label>当前年级：</label>
                            <input
                                type="number"
                                name="current_grade"
                                value={formData.current_grade}
                                onChange={handleInputChange}
                                min="1"
                                max="4"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>当前学期：</label>
                            <input
                                type="number"
                                name="current_semester"
                                value={formData.current_semester}
                                onChange={handleInputChange}
                                min="1"
                                max="2"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>已修课程（用逗号分隔）：</label>
                            <input
                                type="text"
                                name="completed_courses"
                                value={formData.completed_courses}
                                onChange={handleInputChange}
                                required
                            />
                        </div>
                    </>
                )}

                <div className="form-group">
                    <label>
                        <input
                            type="checkbox"
                            name="study_abroad"
                            checked={formData.study_abroad}
                            onChange={handleInputChange}
                        />
                        是否计划出国留学
                    </label>
                </div>

                <div className="form-group">
                    <label>
                        <input
                            type="checkbox"
                            name="internship"
                            checked={formData.internship}
                            onChange={handleInputChange}
                        />
                        是否计划实习
                    </label>
                </div>

                {formData.internship && (
                    <div className="form-group">
                        <label>计划实习学期：</label>
                        <input
                            type="number"
                            name="internship_semester"
                            value={formData.internship_semester}
                            onChange={handleInputChange}
                            min="1"
                            max="8"
                            required
                        />
                    </div>
                )}

                <div className="form-group">
                    <label>每学期光华专业课学分上限：</label>
                    <input
                        type="number"
                        name="upperbound_credits"
                        value={formData.upperbound_credits}
                        onChange={handleInputChange}
                        min="9"
                        max="20"
                        required
                    />
                </div>

                <div className="form-group">
                    <label>总体规划：</label>
                    <select
                        name="planning_type"
                        value={formData.planning_type}
                        onChange={handleInputChange}
                    >
                        {Object.entries(planningTypes).map(([value, label]) => (
                            <option key={value} value={value}>{label}</option>
                        ))}
                    </select>
                </div>

                {formData.planning_type === 'Balanced Workload' && (
                    <div className="form-group">
                        <label>每学期目标学分：</label>
                        <input
                            type="number"
                            name="target_credits_per_semester"
                            value={formData.target_credits_per_semester}
                            onChange={handleInputChange}
                            min="9"
                            max="20"
                            required
                        />
                    </div>
                )}

                <div className="form-group">
                    <label>感兴趣的学科子领域（最多选择3个）：</label>
                    <div className="subject-options">
                        {subjectOptions.map(subject => (
                            <label key={subject} className="subject-option">
                                <input
                                    type="checkbox"
                                    checked={formData.preferred_subjects.includes(subject)}
                                    onChange={() => handleSubjectToggle(subject)}
                                    disabled={!formData.preferred_subjects.includes(subject) && formData.preferred_subjects.length >= 3}
                                />
                                {subject}
                            </label>
                        ))}
                    </div>
                </div>

                <button type="submit" disabled={loading}>
                    {loading ? '生成中...' : '生成选课规划'}
                </button>
            </form>

            {error && <div className="error">{error}</div>}

            {result && (
                <div className="result">
                    <h2>推荐课表</h2>
                    {Object.entries(result.schedule).map(([semester, data]) => (
                        <div key={semester} className="semester-schedule">
                            <h3>第{semester}学期</h3>
                            <p>总学分：{data.total_credits}</p>
                            <div className="courses-list">
                                {data.courses.map((course, index) => (
                                    <div key={index} className="course-item">
                                        <p>{course.name} ({course.credits}学分)</p>
                                        {course.subject_category.length > 0 && (
                                            <p className="course-category">课程类别：{course.subject_category.join(', ')}</p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                    <p className="total-credits">总学分：{result.total_credits}</p>
                    {result.message && <p className="message">{result.message}</p>}
                </div>
            )}
        </div>
    );
}

export default App;