import Stack from '@mui/material/Stack';

import type { IPdfElement } from 'client-types/';

import { PDFElement } from './PDF';
import { Collapse } from 'src/Collapse';
import { HorizontalRule } from '@mui/icons-material';

interface Props {
  items: IPdfElement[];
}

const InlinedPDFList = ({ items }: Props) => (
  <Collapse defaultExpandAll={false} collapsedSize={0} collapseLabel='أخفي المصادر' expandLabel='تفقد المصادر'>
    <Stack spacing={1} sx={{ mt: 2 }}>
      {items.map((pdf, i) => {
        return (
          <div
            key={i}
            style={{
              display: 'flex',
              flexFlow: 'column',
              maxWidth: '600px',
              height: '420px'
            }}
          >
            <div className={`${pdf.display}-pdf-name`}>{pdf.name}</div>
            <PDFElement element={pdf} />
          </div>
        );
      })}
    </Stack>
  </Collapse>
);

export { InlinedPDFList };
