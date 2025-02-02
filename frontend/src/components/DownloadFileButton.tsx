import { DownloadOutlined } from '@ant-design/icons';
import { Button } from 'antd';

import type { Action } from '@/api/chat/types';

interface DownloadFileButtonProps {
  data: Action;
}

const DownloadFileButton: React.FC<DownloadFileButtonProps> = ({ data }) => {
  const handleDownload = () => {
    const { content, filename } = data.params;

    // Create a blob from the content
    const blob = new Blob([content], { type: 'text/plain' });

    // Create a URL for the blob
    const url = window.URL.createObjectURL(blob);

    // Create a temporary anchor element
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'download.txt';

    // Trigger the download
    document.body.appendChild(a);
    a.click();

    // Clean up
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <Button icon={<DownloadOutlined />} onClick={handleDownload}>
      {data.label}
    </Button>
  );
};

export default DownloadFileButton;
