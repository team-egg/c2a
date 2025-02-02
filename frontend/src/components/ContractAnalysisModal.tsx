import React, { useState } from 'react';
import { Modal as AntModal, Form, Input, Select } from 'antd';
import { createStyles } from 'antd-style';

import { BASE_SEPOLIA_CHAIN_ID } from '../constants';

interface ContractAnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (contractAddress: string, network: string) => void;
}

interface NetworkOption {
  id: number;
  name: string;
}

const networks: NetworkOption[] = [
  { id: BASE_SEPOLIA_CHAIN_ID, name: 'Base Sepolia' },
  { id: 8453, name: 'Base' },
];

const useStyles = createStyles(({ token }) => ({
  form: {
    '.ant-form-item-label > label': {
      color: token.colorTextSecondary,
      fontSize: token.fontSizeSM,
    },
  },
  error: {
    color: token.colorError,
    fontSize: token.fontSizeSM,
    marginTop: token.marginXS,
  },
}));

const ContractAnalysisModal: React.FC<ContractAnalysisModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const { styles } = useStyles();
  const [form] = Form.useForm();
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const contractAddress = values.contractAddress as string;

      if (!/^0x[a-fA-F0-9]{40}$/.test(contractAddress)) {
        setError('Invalid contract address format');
        return;
      }

      onSubmit(contractAddress, values.network);
    } catch (err) {
      // Form validation error is handled by antd
    }
  };

  return (
    <AntModal
      title="Contract Analysis"
      open={isOpen}
      onCancel={() => {
        form.resetFields();
        setError('');
        onClose();
      }}
      onOk={handleSubmit}
      okText="Confirm"
      cancelText="Cancel"
    >
      <Form form={form} layout="vertical" className={styles.form} initialValues={{ network: networks[0].name }}>
        <Form.Item
          label="Contract Address"
          name="contractAddress"
          rules={[{ required: true, message: 'Please enter a contract address' }]}
        >
          <Input placeholder="0x..." onChange={() => setError('')} />
        </Form.Item>

        <Form.Item label="Network" name="network">
          <Select>
            {networks.map(network => (
              <Select.Option key={network.id} value={network.name}>
                {network.name}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>

        {error && <div className={styles.error}>{error}</div>}
      </Form>
    </AntModal>
  );
};

export default ContractAnalysisModal;
