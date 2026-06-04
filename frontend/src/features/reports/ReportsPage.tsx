import { DownloadOutlined, FileTextOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Button, Card, List, Spin, Typography } from 'antd';
import ReactMarkdown from 'react-markdown';
import { Link, useParams } from 'react-router-dom';
import { reportsApi } from '@/api';

const { Title, Text } = Typography;

export default function ReportsPage() {
  const { id } = useParams();

  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsApi.list().then((r) => r.data),
    enabled: !id,
  });

  const { data: report, isLoading: reportLoading } = useQuery({
    queryKey: ['report', id],
    queryFn: () => reportsApi.get(Number(id)).then((r) => r.data),
    enabled: !!id,
  });

  const handleDownloadPdf = async (reportId: number) => {
    const { data } = await reportsApi.downloadPdf(reportId);
    const url = window.URL.createObjectURL(new Blob([data]));
    const link = document.createElement('a');
    link.href = url;
    link.download = `report-${reportId}.pdf`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  if (id) {
    if (reportLoading) return <Spin size="large" style={{ display: 'block', margin: '48px auto' }} />;
    if (!report) return <div>리포트를 찾을 수 없습니다.</div>;

    return (
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Title level={2}>{report.title}</Title>
          <Button icon={<DownloadOutlined />} onClick={() => handleDownloadPdf(report.id)}>
            PDF 다운로드
          </Button>
        </div>
        <Text type="secondary">{new Date(report.created_at).toLocaleString('ko-KR')}</Text>
        {report.summary && <Card style={{ margin: '16px 0' }}>{report.summary}</Card>}
        <Card>
          <ReactMarkdown>{report.markdown_content || ''}</ReactMarkdown>
        </Card>
      </div>
    );
  }

  return (
    <div>
      <Title level={2}>Reports</Title>
      <List
        loading={isLoading}
        dataSource={reports}
        renderItem={(item) => (
          <List.Item
            actions={[
              <Link key="view" to={`/reports/${item.id}`}>상세</Link>,
              <Button key="pdf" type="link" icon={<DownloadOutlined />} onClick={() => handleDownloadPdf(item.id)}>
                PDF
              </Button>,
            ]}
          >
            <List.Item.Meta
              avatar={<FileTextOutlined style={{ fontSize: 24 }} />}
              title={<Link to={`/reports/${item.id}`}>{item.title}</Link>}
              description={`${item.analysis_type} · ${new Date(item.created_at).toLocaleDateString('ko-KR')}`}
            />
          </List.Item>
        )}
      />
    </div>
  );
}
