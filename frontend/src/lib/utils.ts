import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

export function validateVideoFile(file: File): { isValid: boolean; error?: string } {
  const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska']
  const maxSize = 100 * 1024 * 1024 // 100MB
  
  if (!validTypes.includes(file.type)) {
    return {
      isValid: false,
      error: 'Invalid file type. Please upload a video file (MP4, AVI, MOV, MKV)'
    }
  }
  
  if (file.size > maxSize) {
    return {
      isValid: false,
      error: 'File too large. Maximum size is 100MB'
    }
  }
  
  return { isValid: true }
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-400'
  if (confidence >= 0.6) return 'text-yellow-400'
  return 'text-red-400'
}

export function getConfidenceLevel(confidence: number): string {
  if (confidence >= 0.9) return 'Very High'
  if (confidence >= 0.8) return 'High'
  if (confidence >= 0.7) return 'Medium-High'
  if (confidence >= 0.6) return 'Medium'
  if (confidence >= 0.5) return 'Medium-Low'
  return 'Low'
}