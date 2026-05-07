/// <reference types="node" />
import { defineConfig } from 'vite'

/** GitHub project Pages: `https://<owner>.github.io/<repo>/` */
function repoBase(): string {
  const gh = process.env.GITHUB_REPOSITORY
  if (gh) {
    const repo = gh.split('/')[1] ?? ''
    return repo ? `/${repo}/` : '/'
  }
  const envBase = process.env.VITE_BASE
  if (envBase) {
    const b = envBase.startsWith('/') ? envBase : `/${envBase}`
    return b.endsWith('/') ? b : `${b}/`
  }
  return '/'
}

export default defineConfig({
  base: repoBase(),
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
