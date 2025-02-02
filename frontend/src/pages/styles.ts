import { createStyles } from 'antd-style';

const useStyle = createStyles(({ css }) => {
  return {
    wrapper: css`
      width: 600px;
      margin: auto;
      padding-top: 30px;
      min-height: 100vh;

      .chat {
        width: 100%;
        &-wallet {
          --ock-bg-secondary: #ffffff;
          --ock-bg-secondary-hover: #ffffff;
        }

        &-container {
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 12px;
          padding-bottom: 40px;
        }
        &-card {
          width: 100%;

          border-radius: 12px;
          border: none;
          &-head {
          }
          &-body {
            overflow: auto;
          }
        }

        &-controller {
          padding: 0 24px;
          &-sender {
          }
          &-actions {
            width: 100%;
            flex-wrap: wrap;
            min-height: 40px;
          }
        }
      }

      .powered-by {
        margin-top: 10px;
        text-align: center;
        color: #999;
      }
    `,
  };
});

export default useStyle;
