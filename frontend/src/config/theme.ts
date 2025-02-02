import { ThemeConfig } from 'antd';
import { createGlobalStyle } from 'antd-style';

const theme: ThemeConfig = {
  token: {},
  components: {},
};

const Global = createGlobalStyle`
* {
  box-sizing: border-box;
}

:root {
}

body {
  background: #f7f7f7;
}

svg {
  display: block;
}

.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.items-center {
  align-items: center;
}

.elp {
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.w-full {
  width: 100%;
}

.h-full {
  height: 100%;
}

.position-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%);
}

.markdown-body {
  h1 {
    font-size: 20px;
  }
  h2 {
    font-size: 18px;
  }
  h3 {
    font-size: 16px;
  }
  h1,h2,h3,ul,ol {
    margin-bottom: 5px;
  }

  ul,ol {
    padding-left: 30px;
  }
  
  ul {
    list-style: disc;
  }
  ol {
    list-style: decimal;
  }

  strong,b {
    font-weight: bold;
  }
  p {
    line-height: 1.6;
  }

  a {
    text-decoration: underline;
  }

  .hljs {
    background: none;
  }
}


`;

export { theme, Global };
