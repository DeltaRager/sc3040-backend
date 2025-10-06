# Creating Authenticated API Endpoints Guide

This guide shows you how to create API endpoints that require authentication in your FastAPI backend and how to call them from your frontend.

## 🔐 **Backend: Creating Authenticated Endpoints**

### **1. Basic Protected Endpoint**

Add this to your `protected_routes.py` or create a new file:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["protected"])

# Example: Get user's learning progress
@router.get("/learning-progress")
async def get_learning_progress(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get user's learning progress - requires authentication
    """
    user_id = current_user["id"]
    
    # Your business logic here
    # Example: Query database for user's progress
    progress_data = {
        "user_id": user_id,
        "lessons_completed": 15,
        "current_level": "Intermediate",
        "total_points": 1250,
        "last_activity": "2024-01-15T10:30:00Z"
    }
    
    return progress_data
```

### **2. POST Endpoint with Data**

```python
from pydantic import BaseModel

class LessonCompletion(BaseModel):
    lesson_id: str
    score: int
    time_spent: int  # in minutes

@router.post("/complete-lesson")
async def complete_lesson(
    lesson_data: LessonCompletion,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Mark a lesson as completed - requires authentication
    """
    user_id = current_user["id"]
    
    # Validate that the user can complete this lesson
    if lesson_data.score < 0 or lesson_data.score > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score must be between 0 and 100"
        )
    
    # Your business logic here
    # Example: Save to database
    completion_record = {
        "user_id": user_id,
        "lesson_id": lesson_data.lesson_id,
        "score": lesson_data.score,
        "time_spent": lesson_data.time_spent,
        "completed_at": "2024-01-15T10:30:00Z"
    }
    
    return {
        "message": "Lesson completed successfully",
        "completion_id": "comp_123456",
        "data": completion_record
    }
```

### **3. PUT Endpoint for Updates**

```python
class ProfileUpdate(BaseModel):
    full_name: str
    learning_goals: str
    preferred_difficulty: str

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user profile - requires authentication
    """
    user_id = current_user["id"]
    
    # Your business logic here
    # Example: Update user profile in database
    updated_profile = {
        "user_id": user_id,
        "full_name": profile_data.full_name,
        "learning_goals": profile_data.learning_goals,
        "preferred_difficulty": profile_data.preferred_difficulty,
        "updated_at": "2024-01-15T10:30:00Z"
    }
    
    return {
        "message": "Profile updated successfully",
        "profile": updated_profile
    }
```

### **4. DELETE Endpoint**

```python
@router.delete("/account")
async def delete_account(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Delete user account - requires authentication
    """
    user_id = current_user["id"]
    
    # Your business logic here
    # Example: Soft delete user account
    # Note: In production, you might want to add additional confirmation
    
    return {
        "message": "Account deleted successfully",
        "deleted_user_id": user_id
    }
```

### **5. Endpoint with Optional Authentication**

```python
from auth import get_current_user_optional

@router.get("/public-lessons")
async def get_public_lessons(current_user: Dict[str, Any] = Depends(get_current_user_optional)):
    """
    Get public lessons - authentication optional
    """
    lessons = [
        {"id": "lesson_1", "title": "Basic Greetings", "difficulty": "Beginner"},
        {"id": "lesson_2", "title": "Numbers 1-10", "difficulty": "Beginner"},
        {"id": "lesson_3", "title": "Family Members", "difficulty": "Intermediate"}
    ]
    
    if current_user:
        # User is authenticated - return personalized data
        return {
            "lessons": lessons,
            "user_progress": {
                "completed_lessons": ["lesson_1"],
                "current_lesson": "lesson_2"
            }
        }
    else:
        # User is not authenticated - return basic data
        return {"lessons": lessons}
```

## 🎯 **Frontend: Calling Authenticated Endpoints**

### **1. Update API Client**

Add new methods to your `App/frontend/src/lib/api.ts`:

```typescript
// Add these methods to your ApiClient class

async getLearningProgress() {
  return this.get('/api/learning-progress');
}

async completeLesson(lessonData: {
  lesson_id: string;
  score: number;
  time_spent: number;
}) {
  return this.post('/api/complete-lesson', lessonData);
}

async updateProfile(profileData: {
  full_name: string;
  learning_goals: string;
  preferred_difficulty: string;
}) {
  return this.put('/api/profile', profileData);
}

async deleteAccount() {
  return this.delete('/api/account');
}

async getPublicLessons() {
  return this.get('/api/public-lessons');
}
```

### **2. Using in React Components**

```typescript
'use client';

import { useState } from 'react';
import { Button, Card, Text, Alert, Stack } from '@mantine/core';
import { apiClient } from '../../lib/api';

export default function LearningProgress() {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProgress = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiClient.getLearningProgress();
      setProgress(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const completeLesson = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiClient.completeLesson({
        lesson_id: 'lesson_123',
        score: 95,
        time_spent: 15
      });
      console.log('Lesson completed:', result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack gap="md">
      <Button onClick={fetchProgress} loading={loading}>
        Get My Progress
      </Button>
      
      <Button onClick={completeLesson} loading={loading} color="green">
        Complete Lesson
      </Button>

      {error && (
        <Alert color="red" title="Error">
          {error}
        </Alert>
      )}

      {progress && (
        <Card>
          <Text>Lessons Completed: {progress.lessons_completed}</Text>
          <Text>Current Level: {progress.current_level}</Text>
          <Text>Total Points: {progress.total_points}</Text>
        </Card>
      )}
    </Stack>
  );
}
```

### **3. Form Submission Example**

```typescript
'use client';

import { useState } from 'react';
import { Button, TextInput, Textarea, Select, Stack } from '@mantine/core';
import { apiClient } from '../../lib/api';

export default function ProfileForm() {
  const [formData, setFormData] = useState({
    full_name: '',
    learning_goals: '',
    preferred_difficulty: 'Beginner'
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const result = await apiClient.updateProfile(formData);
      setMessage('Profile updated successfully!');
      console.log('Updated profile:', result);
    } catch (error: any) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Stack gap="md">
        <TextInput
          label="Full Name"
          value={formData.full_name}
          onChange={(e) => setFormData({...formData, full_name: e.target.value})}
          required
        />
        
        <Textarea
          label="Learning Goals"
          value={formData.learning_goals}
          onChange={(e) => setFormData({...formData, learning_goals: e.target.value})}
          rows={3}
        />
        
        <Select
          label="Preferred Difficulty"
          value={formData.preferred_difficulty}
          onChange={(value) => setFormData({...formData, preferred_difficulty: value || 'Beginner'})}
          data={['Beginner', 'Intermediate', 'Advanced']}
        />
        
        <Button type="submit" loading={loading}>
          Update Profile
        </Button>
        
        {message && <Text color={message.includes('Error') ? 'red' : 'green'}>{message}</Text>}
      </Stack>
    </form>
  );
}
```

## 🔧 **Advanced Patterns**

### **1. Error Handling**

```typescript
// In your API client
async makeRequest(endpoint: string, options: RequestInit = {}): Promise<Response> {
  const token = await this.getAuthToken();
  
  if (!token) {
    throw new Error('No authentication token available');
  }

  const response = await fetch(`${this.baseUrl}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid
      await supabase.auth.signOut();
      window.location.href = '/';
      throw new Error('Authentication expired');
    } else if (response.status === 403) {
      throw new Error('Access forbidden');
    } else if (response.status === 404) {
      throw new Error('Resource not found');
    } else {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed: ${response.status}`);
    }
  }

  return response;
}
```

### **2. Loading States**

```typescript
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [data, setData] = useState<any>(null);

const handleApiCall = async (apiFunction: () => Promise<any>) => {
  setLoading(true);
  setError(null);
  
  try {
    const result = await apiFunction();
    setData(result);
  } catch (err: any) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

### **3. TypeScript Types**

```typescript
// Define types for your API responses
interface LearningProgress {
  user_id: string;
  lessons_completed: number;
  current_level: string;
  total_points: number;
  last_activity: string;
}

interface LessonCompletion {
  lesson_id: string;
  score: number;
  time_spent: number;
}

interface ProfileUpdate {
  full_name: string;
  learning_goals: string;
  preferred_difficulty: string;
}

// Use in your API client
async getLearningProgress(): Promise<LearningProgress> {
  return this.get<LearningProgress>('/api/learning-progress');
}
```

## ✅ **Testing Your Endpoints**

### **1. Test with curl**

```bash
# Get token from browser dev tools (Application > Local Storage > supabase.auth.token)
TOKEN="your_jwt_token_here"

# Test GET endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/learning-progress

# Test POST endpoint
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"lesson_id":"lesson_123","score":95,"time_spent":15}' \
     http://localhost:8000/api/complete-lesson
```

### **2. Test in Frontend**

1. **Login to your app**
2. **Navigate to a page with your new component**
3. **Click buttons to test API calls**
4. **Check browser dev tools** for network requests
5. **Verify responses** in the UI

## 🚀 **Best Practices**

1. **Always validate input** on both frontend and backend
2. **Use proper HTTP status codes** (200, 201, 400, 401, 403, 404, 500)
3. **Handle errors gracefully** with user-friendly messages
4. **Use TypeScript types** for better development experience
5. **Test your endpoints** before deploying
6. **Log important events** for debugging
7. **Use proper authentication** for sensitive operations

Now you can create any authenticated API endpoint and call it from your frontend! 🎉
