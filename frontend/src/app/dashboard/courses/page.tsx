"use client";

import { useEffect, useState } from "react";
import { coursesAPI } from "@/lib/api";

interface Course {
    id: string;
    title: string;
    description: string;
    status: string;
    price: string;
    currency: string;
    section_count: number;
    lesson_count: number;
    enrollment_count: number;
    thumbnail_url: string;
    created_at: string;
}

export default function CoursesPage() {
    const [courses, setCourses] = useState<Course[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [form, setForm] = useState({ title: "", description: "", price: "0" });

    useEffect(() => {
        loadCourses();
    }, []);

    async function loadCourses() {
        setLoading(true);
        try {
            const res = await coursesAPI.list();
            setCourses(res.data?.results || res.data || []);
        } catch (e) {
            console.error("Failed to load courses", e);
        } finally {
            setLoading(false);
        }
    }

    async function createCourse() {
        try {
            await coursesAPI.create({
                title: form.title,
                description: form.description,
                price: form.price,
            });
            setForm({ title: "", description: "", price: "0" });
            setShowCreate(false);
            loadCourses();
        } catch (e) {
            console.error("Failed to create course", e);
        }
    }

    async function publishCourse(id: string) {
        try {
            await coursesAPI.publish(id);
            loadCourses();
        } catch (e) {
            console.error("Failed to publish course", e);
        }
    }

    async function archiveCourse(id: string) {
        if (!confirm("Archive this course?")) return;
        try {
            await coursesAPI.archive(id);
            loadCourses();
        } catch (e) {
            console.error("Failed to archive course", e);
        }
    }

    const statusBadge = (s: string) => {
        const styles: Record<string, string> = {
            draft: "bg-gray-100 text-gray-600",
            published: "bg-green-100 text-green-700",
            archived: "bg-red-100 text-red-600",
        };
        return styles[s] || "bg-gray-100 text-gray-600";
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Courses</h1>
                    <p className="text-gray-500 mt-1">Create and manage online courses, quizzes, and certificates.</p>
                </div>
                <button
                    onClick={() => setShowCreate(!showCreate)}
                    className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                    + New Course
                </button>
            </div>

            {/* Create Form */}
            {showCreate && (
                <div className="mb-6 p-4 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                    <h3 className="font-medium mb-3">New Course</h3>
                    <div className="space-y-3">
                        <input
                            placeholder="Course title"
                            value={form.title}
                            onChange={(e) => setForm({ ...form, title: e.target.value })}
                            className="w-full px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                        />
                        <textarea
                            placeholder="Description"
                            value={form.description}
                            onChange={(e) => setForm({ ...form, description: e.target.value })}
                            className="w-full px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                            rows={3}
                        />
                        <input
                            placeholder="Price (0 for free)"
                            type="number"
                            value={form.price}
                            onChange={(e) => setForm({ ...form, price: e.target.value })}
                            className="w-48 px-3 py-2 border rounded-lg text-sm dark:bg-gray-800 dark:border-gray-600"
                        />
                    </div>
                    <div className="flex gap-2 mt-3">
                        <button onClick={createCourse} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">
                            Create
                        </button>
                        <button onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-gray-500">
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {loading ? (
                <div className="text-center py-20 text-gray-400">Loading...</div>
            ) : courses.length === 0 ? (
                <div className="text-center py-20 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                    <p className="text-5xl mb-4">📚</p>
                    <h2 className="text-xl font-semibold mb-2">No courses yet</h2>
                    <p className="text-gray-500 mb-4">Create your first course with lessons, quizzes, and certificates.</p>
                    <button
                        onClick={() => setShowCreate(true)}
                        className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Create Course
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {courses.map((course) => (
                        <div
                            key={course.id}
                            className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
                        >
                            {/* Thumbnail placeholder */}
                            <div className="h-40 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-3xl">
                                📚
                            </div>
                            <div className="p-4">
                                <div className="flex items-start justify-between mb-2">
                                    <h3 className="font-semibold text-lg">{course.title}</h3>
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge(course.status)}`}>
                                        {course.status}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-500 line-clamp-2 mb-4">{course.description || "No description"}</p>
                                <div className="flex items-center gap-4 text-xs text-gray-400 mb-4">
                                    <span>{course.section_count || 0} sections</span>
                                    <span>{course.lesson_count || 0} lessons</span>
                                    <span>{course.enrollment_count || 0} students</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="font-bold text-lg">
                                        {parseFloat(course.price) > 0 ? `$${course.price}` : "Free"}
                                    </span>
                                    <div className="flex gap-2">
                                        {course.status === "draft" && (
                                            <button
                                                onClick={() => publishCourse(course.id)}
                                                className="px-3 py-1 text-xs bg-green-600 text-white rounded-lg hover:bg-green-700"
                                            >
                                                Publish
                                            </button>
                                        )}
                                        {course.status === "published" && (
                                            <button
                                                onClick={() => archiveCourse(course.id)}
                                                className="px-3 py-1 text-xs border border-gray-300 rounded-lg hover:bg-gray-50"
                                            >
                                                Archive
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
