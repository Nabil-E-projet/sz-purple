// Centralized error normalization and French translation for toast messages
// Supports errors thrown by both src/lib/api.ts and src/api/apiClient.ts

export type ToastVariant = 'default' | 'destructive'

export interface TranslatedError {
  title: string
  description: string
  variant: ToastVariant
  status?: number
  code?: string
}

const fieldLabels: Record<string, string> = {
  email: "Adresse email",
  username: "Nom d'utilisateur",
  password: 'Mot de passe',
  password1: 'Mot de passe',
  password2: 'Confirmation du mot de passe',
  password_confirm: 'Confirmation du mot de passe',
  confirm_password: 'Confirmation du mot de passe',
  new_password: 'Nouveau mot de passe',
  non_field_errors: 'Erreur',
  detail: 'Détail',
}

function isObject(v: any): v is Record<string, any> {
  return v !== null && typeof v === 'object' && !Array.isArray(v)
}

// Common Django error messages translation map
const djangoMessageTranslations: Record<string, string> = {
  'A user with that username already exists.': 'Un utilisateur avec ce nom existe déjà.',
  'User with this email already exists.': 'Un utilisateur avec cet email existe déjà.',
  'A user with that email already exists.': 'Un utilisateur avec cet email existe déjà.',
  'This field is required.': 'Ce champ est obligatoire.',
  'Enter a valid email address.': 'Entrez une adresse email valide.',
  'This password is too short. It must contain at least 8 characters.': 'Ce mot de passe est trop court. Il doit contenir au moins 8 caractères.',
  'This password is too common.': 'Ce mot de passe est trop courant.',
  'This password is entirely numeric.': 'Ce mot de passe ne contient que des chiffres.',
  'The two password fields didn\'t match.': 'Les deux mots de passe ne correspondent pas.',
  'Unable to log in with provided credentials.': 'Nom d\'utilisateur ou mot de passe incorrect.',
  'Invalid token.': 'Token invalide.',
  'Token has expired.': 'Le token a expiré.',
  'User is not active.': 'L\'utilisateur n\'est pas actif.',
  'No active account found with the given credentials': 'Nom d\'utilisateur ou mot de passe incorrect.',
  'Invalid credentials': 'Nom d\'utilisateur ou mot de passe incorrect.',
  'Authentication failed': 'Nom d\'utilisateur ou mot de passe incorrect.',
  'Invalid username or password': 'Nom d\'utilisateur ou mot de passe incorrect.',
}

function translateDjangoMessage(message: string): string {
  // Direct match
  if (djangoMessageTranslations[message]) {
    return djangoMessageTranslations[message]
  }
  
  // Partial match for common patterns
  if (message.includes('already exists')) {
    if (message.includes('username')) return 'Un utilisateur avec ce nom existe déjà.'
    if (message.includes('email')) return 'Un utilisateur avec cet email existe déjà.'
  }
  
  if (message.includes('password') && message.includes('short')) {
    return 'Ce mot de passe est trop court.'
  }
  
  if (message.includes('password') && message.includes('common')) {
    return 'Ce mot de passe est trop courant.'
  }
  
  if (message.includes('password') && message.includes('numeric')) {
    return 'Ce mot de passe ne contient que des chiffres.'
  }
  
  return message // Return original if no translation found
}

function ensureString(v: any): string {
  if (v == null) return ''
  if (typeof v === 'string') {
    return translateDjangoMessage(v)
  }
  try {
    return JSON.stringify(v)
  } catch {
    return String(v)
  }
}

function normalizeShape(err: any): { status?: number; data?: any; code?: string } {
  // From src/lib/api.ts => { status, error }
  if (isObject(err) && (err.status || err.error)) {
    const data = isObject(err.error) || Array.isArray(err.error) ? err.error : (err.error ?? err)
    const code = isObject(data) ? (data.code as string | undefined) : undefined
    return { status: err.status, data, code }
  }

  // From src/api/apiClient.ts => { response: { status, data }, error }
  const status = err?.response?.status
  const data = err?.response?.data ?? err?.error ?? err
  const code = isObject(data) ? (data.code as string | undefined) : undefined
  if (status !== undefined || data !== undefined) return { status, data, code }

  // Fallback
  return { data: err }
}

function buildMessagesFromData(data: any): string[] {
  // Strings
  if (typeof data === 'string') {
    return [data]
  }

  // Arrays of strings
  if (Array.isArray(data)) {
    return data.map(ensureString)
  }

  // Objects (DRF style or custom)
  if (isObject(data)) {
    const messages: string[] = []

    // Common direct keys
    if (typeof data.detail === 'string') messages.push(data.detail)
    if (typeof data.message === 'string') messages.push(data.message)
    if (typeof data.error === 'string') messages.push(data.error)

    // Field-specific errors
    for (const [key, value] of Object.entries(data)) {
      if (['detail', 'message', 'error'].includes(key)) continue
      const label = fieldLabels[key] || key
      if (Array.isArray(value)) {
        const line = `${label}: ${value.map(ensureString).join(', ')}`
        messages.push(line)
      } else if (typeof value === 'string') {
        messages.push(`${label}: ${value}`)
      }
    }

    if (messages.length > 0) return messages
  }

  // Unknown structure
  const txt = ensureString(data)
  return txt ? [txt] : []
}

export function getFrenchError(err: any): TranslatedError {
  const { status, data, code } = normalizeShape(err)

  // Special cases
  if (status === 0) {
    return {
      title: 'Connexion impossible',
      description: "Impossible de contacter le serveur. Vérifiez votre connexion.",
      variant: 'destructive',
      status,
      code,
    }
  }

  if (status === 401) {
    // Check if this is a login error vs session expired
    const dataStr = typeof data === 'string' ? data : JSON.stringify(data || '')
    const isLoginError = dataStr.includes('credentials') || 
                        dataStr.includes('login') || 
                        dataStr.includes('authentication') ||
                        dataStr.includes('Invalid') ||
                        dataStr.includes('Unable to log in')
    
    if (isLoginError) {
      return {
        title: 'Erreur de connexion',
        description: 'Aucun compte n\'existe avec ces informations.',
        variant: 'destructive',
        status,
        code,
      }
    } else {
      return {
        title: 'Session expirée',
        description: 'Veuillez vous reconnecter pour continuer.',
        variant: 'destructive',
        status,
        code,
      }
    }
  }

  if (status === 403) {
    return {
      title: 'Accès refusé',
      description: "Vous n'avez pas les permissions nécessaires pour effectuer cette action.",
      variant: 'destructive',
      status,
      code,
    }
  }

  if (status === 404) {
    const lines = buildMessagesFromData(data)
    const description = lines.length > 0
      ? lines.join('\n')
      : 'La ressource demandée est introuvable.'
    return {
      title: 'Introuvable',
      description,
      variant: 'destructive',
      status,
      code,
    }
  }

  if (status === 402 || code === 'payment_required') {
    return {
      title: 'Crédits insuffisants',
      description: "Veuillez acheter des crédits pour lancer l'analyse.",
      variant: 'destructive',
      status,
      code: code ?? 'payment_required',
    }
  }

  // Generic/validation
  const lines = buildMessagesFromData(data)
  const description = lines.length > 0
    ? lines.join('\n')
    : "Une erreur est survenue. Veuillez réessayer."

  const isValidation = (status === 400 || status === 422) ||
    (isObject(data) && Object.keys(data || {}).some(k => k === 'non_field_errors' || k === 'email' || k.includes('password')))

  return {
    title: isValidation ? 'Erreurs de validation' : 'Erreur',
    description,
    variant: 'destructive',
    status,
    code,
  }
}

export function isPaymentRequired(err: any): boolean {
  const { status, data, code } = normalizeShape(err)
  if (status === 402) return true
  const c = (isObject(data) ? (data.code as string | undefined) : undefined) || code
  return c === 'payment_required'
}
