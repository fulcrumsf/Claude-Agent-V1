/**
 * @typedef {Object} UserProfile
 * @property {string} uid
 * @property {string} email
 * @property {Object} preferences
 * @property {boolean} preferences.notificationsEnabled
 * @property {string} preferences.defaultReminderTime
 */

/**
 * @typedef {'hvac' | 'pool' | 'spa' | 'smoke_detector' | 'other'} AssetType
 */

/**
 * @typedef {Object} Asset
 * @property {string} id
 * @property {string} userId
 * @property {string} name
 * @property {AssetType} type
 * @property {string} location
 * @property {string} [manufacturer]
 * @property {string} [model]
 * @property {string} notes
 * @property {string[]} photos - List of URL strings
 * @property {Date} createdAt
 */

/**
 * @typedef {'fixed_interval' | 'one_time'} FrequencyType
 */

/**
 * @typedef {'upcoming' | 'due' | 'overdue' | 'completed'} TaskStatus
 */

/**
 * @typedef {Object} Task
 * @property {string} id
 * @property {string} userId
 * @property {string | null} assetId
 * @property {string} title
 * @property {string} description
 * @property {FrequencyType} frequencyType
 * @property {number} [intervalDays] - Required if frequencyType is fixed_interval
 * @property {Date} dueDate
 * @property {Date} [lastCompletedAt]
 * @property {TaskStatus} status
 */

export const ASSET_TYPES = ['hvac', 'pool', 'spa', 'smoke_detector', 'other'];
export const TASK_STATUSES = ['upcoming', 'due', 'overdue', 'completed'];
