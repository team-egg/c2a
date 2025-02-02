import hljs from 'highlight.js';
import markdownit from 'markdown-it';

const md = markdownit({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true,
  highlight: function (str, lang) {
    return (
      '<pre class="hljs"><code>' + hljs.highlight(str, { language: lang, ignoreIllegals: true }).value + '</code></pre>'
    );
  },
});

// 存储原始的 renderer.rules.link_open 函数
const defaultRender =
  md.renderer.rules.link_open ||
  function (tokens, idx, options, env, self) {
    return self.renderToken(tokens, idx, options);
  };

// 重写 link_open 规则
md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
  // 为所有链接添加 target="_blank" 和 rel="noopener noreferrer"
  const aIndex = tokens[idx].attrIndex('target');
  const relIndex = tokens[idx].attrIndex('rel');

  if (aIndex < 0) {
    tokens[idx].attrPush(['target', '_blank']);
  } else {
    tokens[idx].attrs![aIndex][1] = '_blank';
  }

  if (relIndex < 0) {
    tokens[idx].attrPush(['rel', 'noopener noreferrer']);
  } else {
    tokens[idx].attrs![relIndex][1] = 'noopener noreferrer';
  }

  // 传递 token 到默认的 renderer
  return defaultRender(tokens, idx, options, env, self);
};

export default md;
