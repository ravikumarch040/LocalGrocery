/**
 * Update these for your organization before publishing.
 */
export const siteConfig = {
  /** Shown in nav + footer */
  brandName: 'LocalGrocery',
  /** Primary CTA — set your sales or hello@ address */
  contactEmail: 'hello@example.com',
  /** Optional: partner booking link (Calendly, Google Calendar, etc.) */
  bookDemoUrl: '',
  /** GitHub repo for issues / community (optional) */
  githubRepoUrl: 'https://github.com/org-or-user/LocalGrocery',
}

export function mailtoContact(subject = 'LocalGrocery demo'): string {
  const s = encodeURIComponent(subject)
  return `mailto:${siteConfig.contactEmail}?subject=${s}`
}
