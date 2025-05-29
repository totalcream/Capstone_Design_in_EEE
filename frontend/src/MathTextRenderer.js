import { MathJax } from 'better-react-mathjax';

export default function MathTextRenderer({ text }) {
  return <MathJax dynamic>{text}</MathJax>;
}
