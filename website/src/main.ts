import './style.css'

import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'

import { mailtoContact, siteConfig } from './site-config'

gsap.registerPlugin(ScrollTrigger)

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

let lenis: Lenis | null = null

function animateDotOnPath(dot: SVGCircleElement, pathSelector: string, durationSec: number): void {
  const path = document.querySelector(pathSelector)
  if (!(path instanceof SVGPathElement)) return
  const len = path.getTotalLength()
  const t0 = performance.now()
  dot.setAttribute('opacity', '0.9')

  const tick = (now: number): void => {
    const elapsed = ((now - t0) / 1000) % durationSec
    const p = elapsed / durationSec
    const pt = path.getPointAtLength(p * len)
    dot.setAttribute('cx', String(pt.x))
    dot.setAttribute('cy', String(pt.y))
    requestAnimationFrame(tick)
  }
  requestAnimationFrame(tick)
}

function initLenis(): void {
  if (prefersReducedMotion) return
  lenis = new Lenis({ duration: 1.1 })
  lenis.on('scroll', ScrollTrigger.update)
  gsap.ticker.add((time) => {
    lenis?.raf(time * 1000)
  })
  gsap.ticker.lagSmoothing(0)
}

function smoothScrollTo(target: HTMLElement): void {
  const headerOffset = 72
  if (lenis) {
    lenis.scrollTo(target, { offset: -headerOffset })
    return
  }
  const top = target.getBoundingClientRect().top + window.scrollY - headerOffset
  window.scrollTo({ top, behavior: prefersReducedMotion ? 'auto' : 'smooth' })
}

function initSmoothAnchors(): void {
  document.querySelectorAll<HTMLAnchorElement>('[data-smooth]').forEach((a) => {
    const href = a.getAttribute('href')
    if (!href || !href.startsWith('#')) return
    a.addEventListener('click', (e) => {
      const sel = href
      const el = document.querySelector(sel)
      if (!(el instanceof HTMLElement)) return
      e.preventDefault()
      smoothScrollTo(el)
    })
  })
}

function wireContact(): void {
  const mail = document.getElementById('cta-mailto')
  if (mail instanceof HTMLAnchorElement) mail.href = mailtoContact()

  const gh = document.getElementById('cta-github')
  if (gh instanceof HTMLAnchorElement) gh.href = siteConfig.githubRepoUrl

  if (siteConfig.bookDemoUrl) {
    const wrap = document.querySelector('#contact .mt-10.flex')
    if (wrap instanceof HTMLElement) {
      const demo = document.createElement('a')
      demo.href = siteConfig.bookDemoUrl
      demo.target = '_blank'
      demo.rel = 'noreferrer'
      demo.className =
        'inline-flex items-center justify-center rounded-full bg-citrus-500 px-6 py-3.5 text-center text-base font-semibold text-ink shadow-card transition hover:-translate-y-0.5 hover:bg-citrus-600'
      demo.textContent = 'Book a demo'
      wrap.prepend(demo)
    }
  }
}

function initHeader(): void {
  const header = document.querySelector<HTMLElement>('[data-header]')
  if (!header) return

  const apply = (scroll: number): void => {
    header.classList.toggle('shadow-soft', scroll > 16)
  }

  if (lenis) {
    lenis.on('scroll', (e: { scroll: number }) => {
      apply(e.scroll)
    })
  } else {
    window.addEventListener('scroll', () => apply(window.scrollY), { passive: true })
  }
  apply(typeof window.scrollY === 'number' ? window.scrollY : 0)
}

function initPersonas(): void {
  const tabs = document.querySelectorAll<HTMLButtonElement>('[data-persona-tab]')
  const panels = document.querySelectorAll<HTMLElement>('[data-persona-panel]')

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const id = tab.getAttribute('data-persona-tab')
      if (!id) return

      tabs.forEach((t) => {
        const active = t === tab
        t.setAttribute('aria-selected', String(active))
        if (active) t.setAttribute('data-active', 'true')
        else t.removeAttribute('data-active')
      })

      panels.forEach((panel) => {
        const match = panel.getAttribute('data-persona-panel') === id
        panel.hidden = !match
        panel.classList.toggle('hidden', !match)
      })
    })
  })
}

function initReveals(): void {
  const revealEls = gsap.utils.toArray<HTMLElement>('.reveal')
  revealEls.forEach((el) => {
    gsap.fromTo(
      el,
      { opacity: prefersReducedMotion ? 1 : 0, y: prefersReducedMotion ? 0 : 36 },
      {
        opacity: 1,
        y: 0,
        duration: prefersReducedMotion ? 0 : 0.9,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: el,
          start: 'top 90%',
          toggleActions: 'play none none none',
        },
      },
    )
  })

  gsap.utils.toArray<HTMLElement>('.bento-card').forEach((el, i) => {
    gsap.fromTo(
      el,
      { opacity: prefersReducedMotion ? 1 : 0, scale: prefersReducedMotion ? 1 : 0.97 },
      {
        opacity: 1,
        scale: 1,
        duration: prefersReducedMotion ? 0 : 0.75,
        delay: prefersReducedMotion ? 0 : i * 0.05,
        ease: 'back.out(1.25)',
        scrollTrigger: {
          trigger: el,
          start: 'top 92%',
          toggleActions: 'play none none none',
        },
      },
    )
  })
}

function initJourney(): void {
  const line = document.getElementById('journey-line')
  if (line && !prefersReducedMotion) {
    gsap.fromTo(
      line,
      { scaleY: 0.05, transformOrigin: 'top center' },
      {
        scaleY: 1,
        ease: 'none',
        scrollTrigger: {
          trigger: '#journey',
          start: 'top 75%',
          end: 'bottom 55%',
          scrub: 0.6,
        },
      },
    )
  }

  gsap.utils.toArray<HTMLElement>('.journey-step').forEach((step, i) => {
    const textCol = step.querySelector('.journey-copy')
    const img = step.querySelector('img')
    const targets = [textCol, img].filter((n): n is Element => n instanceof Element)
    if (!prefersReducedMotion && targets.length) {
      gsap.fromTo(
        targets,
        { opacity: 0, x: i % 2 === 0 ? -28 : 28 },
        {
          opacity: 1,
          x: 0,
          duration: 0.85,
          stagger: 0.12,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: step,
            start: 'top 82%',
            toggleActions: 'play none none none',
          },
        },
      )
    }
  })
}

function initArchitecture(): void {
  const wrap = document.getElementById('arch-wrap')
  if (!wrap) return

  const paths = document.querySelectorAll<SVGPathElement>('.arch-path')
  paths.forEach((path) => {
    const plen = path.getTotalLength()
    path.setAttribute('stroke-dasharray', `${plen}`)
    if (prefersReducedMotion) {
      path.setAttribute('stroke-dashoffset', '0')
      return
    }
    path.setAttribute('stroke-dashoffset', `${plen}`)
    gsap.to(path, {
      strokeDashoffset: 0,
      ease: 'none',
      scrollTrigger: {
        trigger: '#arch-wrap',
        start: 'top 72%',
        end: 'bottom 40%',
        scrub: 1,
      },
    })
  })

  const chapters = document.querySelectorAll<HTMLElement>('[data-chapter]')
  if (chapters.length && !prefersReducedMotion) {
    ScrollTrigger.create({
      trigger: '#arch-wrap',
      start: 'top center',
      end: 'bottom center',
      scrub: true,
      onUpdate(self) {
        const p = self.progress
        chapters.forEach((ch, i) => {
          const n = chapters.length
          const start = i / n
          const active = p >= start && p < (i + 1) / n + 0.0001
          ch.classList.toggle('opacity-100', active)
          ch.classList.toggle('ring-2', active)
          ch.classList.toggle('ring-citrus-400/80', active)
          ch.classList.toggle('opacity-40', !active)
        })
      },
    })
  } else if (chapters.length) {
    chapters.forEach((ch) => ch.classList.add('opacity-100'))
  }

  const dotA = document.getElementById('arch-dot-a')
  const dotB = document.getElementById('arch-dot-b')
  if (!prefersReducedMotion && dotA instanceof SVGCircleElement && dotB instanceof SVGCircleElement) {
    animateDotOnPath(dotA, '#path-c-gw', 5.5)
    animateDotOnPath(dotB, '#path-core-map', 3.8)
  } else if (dotA && dotB) {
    dotA.style.display = 'none'
    dotB.style.display = 'none'
  }
}

function setYear(): void {
  const y = document.getElementById('y')
  if (y) y.textContent = String(new Date().getFullYear())
}

function pauseVideoIfReduced(): void {
  if (!prefersReducedMotion) return
  document.querySelectorAll('video').forEach((v) => {
    v.pause()
    v.removeAttribute('autoplay')
  })
}

function init(): void {
  initLenis()
  initSmoothAnchors()
  wireContact()
  initHeader()
  initPersonas()
  pauseVideoIfReduced()
  setYear()
  initReveals()
  initJourney()
  initArchitecture()

  window.addEventListener('load', () => ScrollTrigger.refresh())
}

init()
