import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'stride',
  description: 'All the speed. None of the mess. Claude Code skills for atomic commits and Linear workflow.',
  base: '/stride/',
  themeConfig: {
    nav: [
      { text: 'Guide', link: '/getting-started' },
      { text: 'Skills', items: [
        { text: '/vision', link: '/skills/vision' },
        { text: '/commit', link: '/skills/commit' },
        { text: '/linear', link: '/skills/linear' },
        { text: '/craft', link: '/skills/craft' },
      ]},
      { text: 'GitHub', link: 'https://github.com/webventurer/stride' },
    ],
    sidebar: [
      {
        text: 'Guide',
        items: [
          { text: 'Why Stride?', link: '/why-stride' },
          { text: 'Getting started', link: '/getting-started' },
          { text: 'How it works', link: '/how-it-works' },
          { text: 'Install', link: '/install' },
        ],
      },
      {
        text: 'Skills',
        items: [
          { text: '/vision — Project vision', link: '/skills/vision' },
          { text: '/commit — Atomic commits', link: '/skills/commit' },
          { text: '/linear — Linear workflow', link: '/skills/linear' },
          { text: '/craft — Prompt generation', link: '/skills/craft' },
        ],
      },
      {
        text: 'Patterns',
        items: [
          { text: 'Friction Distinction', link: '/patterns/friction-distinction' },
          { text: "Revise, don't stretch", link: '/patterns/revise-dont-stretch' },
        ],
      },
      {
        text: 'Reference',
        items: [
          { text: 'Agentic engineering', link: '/reference/agentic-engineering' },
          { text: "Can't we just use Lovable?", link: '/reference/cant-we-just-use-lovable' },
          { text: 'Epics and stories', link: '/reference/epics-and-user-stories' },
          { text: 'Example: Epic card', link: '/reference/example-epic-card' },
          { text: 'Example: Story card', link: '/reference/example-story-card' },
          { text: 'Kanban process', link: '/reference/kanban' },
          { text: 'Issue statuses', link: '/reference/issue-statuses' },
          { text: 'Issue template', link: '/reference/issue-template' },
          { text: 'Chris Beams commit style', link: '/reference/commit-style' },
          { text: 'Migration skills', link: '/reference/migration-skills' },
        ],
      },
      {
        text: 'Research',
        items: [
          { text: 'Sprint vs kanban', link: '/research/agile/sprint-vs-kanban' },
          { text: 'What agile really means', link: '/research/agile/what-agile-really-means' },
        ],
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/webventurer/stride' },
    ],
  },
})
