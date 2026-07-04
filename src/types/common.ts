/**
 * 通用类型定义
 */

/** 统一 API 响应结构 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/** 通用选项（下拉框、页签等） */
export interface OptionItem {
  label: string
  value: string
}

/** 通用键值对项 */
export interface KeyValueItem {
  key: string
  value: string
}
