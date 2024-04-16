import React from 'react';
import styled from 'styled-components';

const VehicleInfo = styled.div`
  font-family: Arial;
`;

const AttributeRow = styled.div`
  margin-bottom: 5px;
`;

const AttributeName = styled.span`
  font-weight: bold;
`;

export default ({ info }) => (
  <VehicleInfo>
    <AttributeRow>
      <AttributeName>Smartcar Vehicle ID:</AttributeName> {info.id}
    </AttributeRow>
    <AttributeRow>
      <AttributeName>Vehicle Make:</AttributeName> {info.make}
    </AttributeRow>
    <AttributeRow>
      <AttributeName>Vehicle Model:</AttributeName> {info.model}
    </AttributeRow>
    <AttributeRow>
      <AttributeName>Vehicle Year:</AttributeName> {info.year}
    </AttributeRow>
  </VehicleInfo>
);