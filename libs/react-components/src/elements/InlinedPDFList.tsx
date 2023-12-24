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
              maxWidth: '600px',
              height: '400px'
            }}
          >
            <PDFElement element={pdf} />
          </div>
        );
      })}
    </Stack>
  </Collapse>
);

export { InlinedPDFList };
